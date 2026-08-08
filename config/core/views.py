from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone

from .models import (
    Skill,
    Task,
    Assessment,
    Submission,
    Evaluation,
    Certificate,
)

from accounts.models import Profile

from .ai import (
    generate_assessment_tasks,
    evaluate_submission,
)

from .utils import generate_qr
from django.urls import reverse

def home(request):
    return redirect("dashboard")


@login_required
def dashboard(request):

    skills = Skill.objects.all()

    assessments = Assessment.objects.filter(
        user=request.user
    ).order_by("-started_at")

    certificates = Certificate.objects.filter(
        user=request.user
    ).order_by("-issued_at")

    context = {
        "skills": skills,
        "assessments": assessments,
        "certificates": certificates,
    }

    return render(
        request,
        "core/dashboard.html",
        context
    )


@login_required
def skill_list(request):

    skills = Skill.objects.all()

    return render(
        request,
        "core/skills.html",
        {
            "skills": skills
        }
    )


@login_required
def skill_detail(request, skill_id):

    skill = get_object_or_404(
        Skill,
        id=skill_id
    )

    return render(
        request,
        "core/skill_detail.html",
        {
            "skill": skill
        }
    )

@login_required
def start_assessment(request, skill_id):

    skill = get_object_or_404(
        Skill,
        id=skill_id
    )

    # Create assessment
    assessment = Assessment.objects.create(
        user=request.user,
        skill=skill
    )

    try:

        # Ask Gemini to generate 5 questions
        result = generate_assessment_tasks(
            skill
        )

        generated_tasks = result.get(
            "tasks",
            []
        )

        if len(generated_tasks) < 5:

            assessment.delete()

            return HttpResponse(
                "AI generated fewer than 5 questions. "
                "Please try again."
            )

        # Create exactly 5 Task records
        task_ids = []

        for item in generated_tasks[:5]:

            task = Task.objects.create(
                skill=skill,
                title=item["title"][:500],
                question=item["question"],
                difficulty=item.get(
                    "difficulty",
                    "Medium"
                ),
                topic=item.get(
                    "topic",
                    ""
                )[:300],
                max_score=100,
            )

            task_ids.append(task.id)

        # Store question IDs for THIS assessment
        request.session[
            f"assessment_{assessment.id}_tasks"
        ] = task_ids

        request.session.modified = True

    except Exception as e:

        print(
            "Assessment generation error:",
            e
        )

        assessment.delete()

        return HttpResponse(
            "Could not generate the assessment. "
            "Please try again."
        )

    return redirect(
        "assessment_question",
        assessment_id=assessment.id,
        question_number=1
    )

@login_required
def assessment_question(
    request,
    assessment_id,
    question_number
):

    assessment = get_object_or_404(
        Assessment,
        id=assessment_id,
        user=request.user
    )

    # Get generated task IDs
    task_ids = request.session.get(
        f"assessment_{assessment.id}_tasks"
    )

    if not task_ids:

        return HttpResponse(
            "Assessment questions could not be found."
        )

    # Make sure question number is valid
    if question_number < 1 or question_number > 5:

        return redirect(
            "assessment_result",
            assessment_id=assessment.id
        )

    # Get task ID
    task_id = task_ids[
        question_number - 1
    ]

    task = get_object_or_404(
        Task,
        id=task_id,
        skill=assessment.skill
    )

    # Handle answer
    if request.method == "POST":

        answer = request.POST.get(
            "answer",
            ""
        ).strip()

        if not answer:

            return render(
                request,
                "core/assessment_question.html",
                {
                    "assessment": assessment,
                    "task": task,
                    "question_number": question_number,
                    "total_questions": 5,
                    "error": "Please enter your answer."
                }
            )

        # Don't allow duplicate submission
        existing_submission = Submission.objects.filter(
            assessment=assessment,
            task=task
        ).first()

        if not existing_submission:

            Submission.objects.create(
                assessment=assessment,
                user=request.user,
                task=task,
                answer=answer
            )

        # Go to next question
        if question_number < 5:

            return redirect(
                "assessment_question",
                assessment_id=assessment.id,
                question_number=question_number + 1
            )

        # All 5 answered
        return redirect(
            "loading_evaluation",
            assessment_id=assessment.id
        )

    return render(
        request,
        "core/assessment_question.html",
        {
            "assessment": assessment,
            "task": task,
            "question_number": question_number,
            "total_questions": 5
        }
    )

@login_required
def evaluate_assessment(
    request,
    assessment_id
):

    assessment = get_object_or_404(
        Assessment,
        id=assessment_id,
        user=request.user
    )

    # Don't evaluate twice
    if assessment.completed_at:

        return redirect(
            "assessment_result",
            assessment_id=assessment.id
        )

    submissions = Submission.objects.filter(
        assessment=assessment
    ).select_related(
        "task"
    ).order_by(
        "submitted_at"
    )

    # Must have exactly 5 answers
    if submissions.count() < 5:

        return HttpResponse(
            "Assessment is incomplete. "
            "Please answer all 5 questions."
        )

    total_score = 0

    for submission in submissions:

        try:

            result = evaluate_submission(
                submission.task,
                submission.answer
            )

            score = int(
                result.get(
                    "score",
                    0
                )
            )

            # Keep score between 0 and 100
            score = max(
                0,
                min(score, 100)
            )

            Evaluation.objects.update_or_create(
                submission=submission,
                defaults={
                    "score": score,

                    "feedback": result.get(
                        "feedback",
                        ""
                    ),

                    "strengths": result.get(
                        "strengths",
                        ""
                    ),

                    "weaknesses": result.get(
                        "weaknesses",
                        ""
                    ),

                    "suggestions": result.get(
                        "suggestions",
                        ""
                    ),

                    "integrity_score": 100,
                }
            )

            total_score += score

        except Exception as e:

            print(
                "AI evaluation error:",
                e
            )

            return HttpResponse(
                "AI evaluation failed. "
                "Please try again."
            )

    # Calculate average
    final_score = round(
        total_score /
        submissions.count()
    )

    # Determine pass/fail
    passed = (
        final_score >=
        assessment.skill.passing_score
    )

    assessment.score = final_score
    assessment.passed = passed
    assessment.completed_at = timezone.now()

    assessment.save()

    # Create certificate if passed
    if passed:

        Certificate.objects.get_or_create(
            assessment=assessment,
            defaults={
                "user": request.user,
                "skill": assessment.skill,
            }
        )
    # Remove temporary session data
    request.session.pop(
        f"assessment_{assessment.id}_tasks",
        None
    )

    request.session.modified = True

    return redirect(
        "assessment_result",
        assessment_id=assessment.id
    )

@login_required
def assessment_result(
    request,
    assessment_id
):

    assessment = get_object_or_404(
        Assessment,
        id=assessment_id,
        user=request.user
    )

    submissions = Submission.objects.filter(
        assessment=assessment
    ).select_related(
        "task"
    ).order_by(
        "submitted_at"
    )

    certificate = Certificate.objects.filter(
        assessment=assessment
    ).first()

    results = []

    for submission in submissions:

        evaluation = Evaluation.objects.filter(
            submission=submission
        ).first()

        results.append({
            "task": submission.task,
            "submission": submission,
            "evaluation": evaluation,
        })

    return render(
        request,
        "core/assessment_result.html",
        {
            "assessment": assessment,
            "results": results,
            "certificate": certificate,
        }
    )

# @login_required
# def certificates(request):

#     certificates = Certificate.objects.filter(
#         user=request.user
#     )

#     return HttpResponse(
#         "<h1>Certificates</h1>"
#         + "".join(
#             f"<p>{certificate.skill.name} - "
#             f"{certificate.minted}</p>"
#             for certificate in certificates
#         )
#     )

@login_required
def certificate_detail(request, certificate_id):

    certificate = get_object_or_404(
        Certificate,
        id=certificate_id,
        user=request.user
    )

    profile = request.user.profile

    return render(
        request,
        "core/certificate.html",
        {
            "certificate": certificate,
            "profile": profile
        }
    )

from django.contrib import messages
from .models import Certificate
from .blockchain import mint_certificate


@login_required
def mint_certificate_view(request, certificate_id):

    certificate = get_object_or_404(
        Certificate,
        id=certificate_id,
        user=request.user,
    )

    if certificate.minted:
        messages.info(
            request,
            "Certificate already minted."
        )
        return redirect(
            "certificate_detail",
            certificate.id,
        )

    wallet = request.user.profile.wallet_address
    

    if not wallet:
        messages.error(
            request,
            "Wallet address not found."
        )
        return redirect(
            "certificate_detail",
            certificate.id,
        )

    print("=== MINT STARTED ===")

    wallet = request.user.profile.wallet_address
    print("Wallet:", wallet)

    try:
        result = mint_certificate(
            recipient_wallet=wallet,
            candidate_name=request.user.get_full_name() or request.user.username,
            skill=certificate.skill.name,
            score=certificate.assessment.score,
        )

    except Exception as e:

        messages.error(
            request,
            f"Blockchain mint failed: {e}"
        )
        print(e)

        return redirect(
            "certificate_detail",
            certificate.id,
        )

    
    if result["token_id"]:
        certificate.token_id = result["token_id"]

    certificate.transaction_hash = result[
        "transaction_hash"
    ]

    certificate.minted = True

    certificate.wallet_address = wallet

    verification_url = request.build_absolute_uri(

        reverse(
            "verify_certificate",
            args=[certificate.id]
        )

    )

    certificate.qr_code.save(

        f"certificate_{certificate.id}.png",

        generate_qr(
            verification_url
        ),

        save=False

    )

    certificate.save()

    messages.success(
        request,
        "🎉 Certificate minted successfully on Sepolia Blockchain."
    )
    return redirect(
        "certificate_detail",
        certificate.id,
    )

import json
from django.http import JsonResponse

@login_required
def save_wallet(request):

    data = json.loads(request.body)

    wallet = data["wallet"]

    profile = request.user.profile

    profile.wallet_address = wallet

    profile.save()

    return JsonResponse({
        "success": True
    })

def verify_certificate(request, certificate_id):

    certificate = get_object_or_404(
        Certificate.objects.select_related(
            "user",
            "skill",
            "assessment",
        ),
        id=certificate_id,
        minted=True,
    )

    return render(
        request,
        "core/verify_certificate.html",
        {
            "certificate": certificate,
        },
    )

from web3 import Web3

@login_required
def save_wallet_manual(request):

    if request.method == "POST":

        wallet = request.POST.get("wallet")

        if not Web3.is_address(wallet):

            messages.error(
                request,
                "Invalid wallet address."
            )

            return redirect("profile")

        if Profile.objects.filter(
            wallet_address__iexact=wallet
        ).exclude(
            user=request.user
        ).exists():

            messages.error(
                request,
                "This wallet is already linked to another account."
            )

            return redirect("profile")

        profile = request.user.profile

        profile.wallet_address = Web3.to_checksum_address(wallet)

        profile.save()

        messages.success(
            request,
            "Wallet saved successfully."
        )

    return redirect("accounts:profile")

from io import BytesIO

from django.http import HttpResponse

from django.template.loader import get_template

from xhtml2pdf import pisa

@login_required
def download_certificate(
    request,
    certificate_id
):

    certificate = get_object_or_404(

        Certificate,

        id=certificate_id,

        user=request.user

    )

    template = get_template(
        "core/certificate_pdf.html"
    )

    html = template.render({

        "certificate": certificate

    })

    pdf = BytesIO()

    pisa.CreatePDF(
        html,
        dest=pdf
    )

    response = HttpResponse(
        pdf.getvalue(),
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (

        f'attachment; filename="Certificate_{certificate.id}.pdf"'

    )

    return response

@login_required
def loading_questions_view(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    return render(request, "core/loading_questions.html", {"skill": skill})

@login_required
def loading_evaluation_view(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
    return render(request, "core/loading_evaluation.html", {"assessment": assessment})
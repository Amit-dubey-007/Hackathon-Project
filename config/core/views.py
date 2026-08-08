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
    evaluate_assessment_batch,
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
                title=item.get("title", "Practical Task")[:500],
                question=item.get("question", ""),
                difficulty=item.get("difficulty", "Medium"),
                topic=item.get("topic", "")[:300],
                max_score=100,
            )

            task_ids.append(task.id)
            
            # Save estimated time in session as UI metadata
            request.session[f"task_{task.id}_time"] = item.get("estimated_time", "15 mins")

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
    
    estimated_time = request.session.get(f"task_{task.id}_time", "15 mins")

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
                    "estimated_time": estimated_time,
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
            "total_questions": 5,
            "estimated_time": estimated_time
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

    # Batch AI evaluation
    from .ai import evaluate_assessment_batch
    from django.contrib import messages

    try:
        batch_result = evaluate_assessment_batch(assessment, submissions)
    except Exception as e:
        print("AI batch evaluation error:", e)
        messages.error(request, "AI evaluation failed. Please try again later.")
        return redirect("dashboard")

    # Overall summary
    overall_score = int(batch_result.get("overall_score", 0))
    overall_score = max(0, min(overall_score, 100))
    
    # Store overall summary in session for results page
    request.session[f"assessment_{assessment.id}_overall"] = {
        "score": overall_score,
        "feedback": batch_result.get("overall_feedback", ""),
        "strengths": batch_result.get("overall_strengths", ""),
        "weaknesses": batch_result.get("overall_weaknesses", ""),
        "suggestions": batch_result.get("overall_suggestions", "")
    }

    # Task evaluations
    returned_tasks = batch_result.get("tasks", [])
    
    for i, submission in enumerate(submissions):
        if i < len(returned_tasks):
            t_res = returned_tasks[i]
            score = max(0, min(int(t_res.get("score", 0)), 100))
            
            Evaluation.objects.update_or_create(
                submission=submission,
                defaults={
                    "score": score,
                    "feedback": t_res.get("feedback", ""),
                    "strengths": t_res.get("strengths", ""),
                    "weaknesses": t_res.get("weaknesses", ""),
                    "suggestions": t_res.get("suggestions", ""),
                    "integrity_score": 100,
                }
            )
        else:
            Evaluation.objects.update_or_create(
                submission=submission,
                defaults={
                    "score": 0,
                    "feedback": "Evaluation details missing.",
                    "integrity_score": 100,
                }
            )

    # Determine pass/fail based on overall_score
    passed = (
        overall_score >=
        assessment.skill.passing_score
    )

    assessment.score = overall_score
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

    overall_summary = request.session.get(f"assessment_{assessment.id}_overall", None)

    return render(
        request,
        "core/assessment_result.html",
        {
            "assessment": assessment,
            "results": results,
            "certificate": certificate,
            "overall_summary": overall_summary,
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
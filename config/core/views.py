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

from .utils import generate_qr_base64
from django.urls import reverse

def home(request):
    return render(request,"core/home.html")

@login_required
def dashboard(request):

    skills = Skill.objects.all()[:6]

    assessments = Assessment.objects.filter(
        user=request.user
    ).order_by("-started_at")[:7]

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


from django.db.models import Q
from django.core.paginator import Paginator

ICON_MAPPING = {
    'html': 'bi-filetype-html text-orange-500',
    'css': 'bi-filetype-css text-blue-500',
    'javascript': 'bi-filetype-js text-yellow-500',
    'js': 'bi-filetype-js text-yellow-500',
    'typescript': 'bi-filetype-tsx text-blue-400',
    'python': 'bi-filetype-py text-blue-500',
    'django': 'bi-terminal-fill text-green-600',
    'react': 'bi-filetype-jsx text-cyan-400',
    'node': 'bi-box-seam-fill text-green-500',
    'docker': 'bi-box-fill text-blue-400',
    'git': 'bi-git text-orange-600',
    'aws': 'bi-cloud-fill text-orange-400',
    'ethereum': 'bi-database-fill-gear text-purple-400',
    'solidity': 'bi-safe-fill text-purple-500',
    'mongodb': 'bi-database-fill text-green-500',
    'postgresql': 'bi-database-fill text-blue-600',
    'postgres': 'bi-database-fill text-blue-600',
    'tenser': 'bi-cpu-fill text-red-500',
    'tensor': 'bi-cpu-fill text-red-500',
    'machine learning': 'bi-brain text-purple-400',
    'cybersecurity': 'bi-shield-lock-fill text-red-500',
    'security': 'bi-shield-lock-fill text-red-500',
}

def get_skill_icon(skill):
    name_lower = skill.name.lower()
    for key, val in ICON_MAPPING.items():
        if key in name_lower:
            return val
    category = skill.category
    if category == 'Frontend':
        return 'bi-display text-blue-400'
    elif category == 'Backend':
        return 'bi-server text-indigo-400'
    elif category == 'Database':
        return 'bi-database text-cyan-400'
    elif category == 'AI':
        return 'bi-cpu text-purple-400'
    elif category == 'Blockchain':
        return 'bi-box text-pink-400'
    elif category == 'Cloud':
        return 'bi-cloud text-blue-400'
    elif category == 'Cybersecurity':
        return 'bi-shield-check text-red-400'
    return 'bi-terminal text-slate-400'

def skill_list(request):
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    difficulty_filter = request.GET.get('difficulty', '').strip()
    status_filter = request.GET.get('status', '').strip()
    sort_by = request.GET.get('sort', '').strip()

    skills = Skill.objects.all()

    passed_skills_ids = set()
    completed_skills_ids = set()
    has_cert_skills_ids = set()

    if request.user.is_authenticated:
        assessments = Assessment.objects.filter(user=request.user)
        completed_assessments = assessments.filter(completed_at__isnull=False)
        completed_skills_ids = set(completed_assessments.values_list('skill_id', flat=True))
        passed_skills_ids = set(completed_assessments.filter(passed=True).values_list('skill_id', flat=True))
        
        certs = Certificate.objects.filter(user=request.user)
        has_cert_skills_ids = set(certs.values_list('skill_id', flat=True))

    if search_query:
        skills = skills.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    if category_filter and category_filter != 'All':
        skills = skills.filter(category__iexact=category_filter)

    if difficulty_filter and difficulty_filter != 'All':
        skills = skills.filter(difficulty__iexact=difficulty_filter)

    if status_filter and status_filter != 'All' and request.user.is_authenticated:
        if status_filter == 'completed':
            skills = skills.filter(id__in=completed_skills_ids)
        elif status_filter == 'passed':
            skills = skills.filter(id__in=passed_skills_ids)
        elif status_filter == 'not_completed':
            skills = skills.exclude(id__in=completed_skills_ids)

    if sort_by == 'az':
        skills = skills.order_by('name')
    elif sort_by == 'za':
        skills = skills.order_by('-name')
    elif sort_by == 'score_low':
        skills = skills.order_by('passing_score')
    elif sort_by == 'score_high':
        skills = skills.order_by('-passing_score')
    elif sort_by == 'newest':
        skills = skills.order_by('-id')
    elif sort_by == 'oldest':
        skills = skills.order_by('id')

    annotated_skills = []
    for skill in skills:
        status = 'not_completed'
        if skill.id in passed_skills_ids:
            status = 'passed'
        elif skill.id in completed_skills_ids:
            status = 'completed'
            
        annotated_skills.append({
            'obj': skill,
            'id': skill.id,
            'name': skill.name,
            'description': skill.description,
            'passing_score': skill.passing_score,
            'category': skill.category,
            'difficulty': skill.difficulty,
            'status': status,
            'has_certificate': skill.id in has_cert_skills_ids,
            'icon': get_skill_icon(skill)
        })

    stats = {
        'total_skills': Skill.objects.count(),
        'completed_skills': len(completed_skills_ids),
        'available_certs': len(has_cert_skills_ids),
        'total_assessments': Assessment.objects.count()
    }

    per_page = 12
    paginator = Paginator(annotated_skills, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    categories = ['Frontend', 'Backend', 'AI', 'Blockchain', 'Cloud', 'Cybersecurity', 'Database', 'Programming Languages']

    for item in page_obj:
        assessment = (
            Assessment.objects
            .filter(user=request.user, skill=item["obj"], passed=True)
            .order_by("-completed_at")
            .first()
        )
        item["latest_assessment"] = assessment

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'difficulty_filter': difficulty_filter,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'stats': stats,
        'categories': categories,
    }

    return render(request, "core/skills.html", context)


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
def integrity_agreement(request, skill_id):
    skill = get_object_or_404(
        Skill,
        id=skill_id
    )
    return render(
        request,
        "core/integrity_agreement.html",
        {"skill": skill}
    )
import logging
import traceback
logger = logging.getLogger(__name__)
@login_required
def start_assessment(request, skill_id):

    skill = get_object_or_404(
        Skill,
        id=skill_id
    )

    # Create assessment
    start_time = timezone.now()
    end_time = start_time + timezone.timedelta(minutes=skill.duration)
    assessment = Assessment.objects.create(
        user=request.user,
        skill=skill,
        start_time=start_time,
        end_time=end_time
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
                task_type=item.get("type", "text")[:10],
                language=item.get("language", "")[:50],
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

        # logger.exception("START ASSESSMENT FAILED")

        # print(traceback.format_exc())

        # raise

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

    if assessment.completed_at:
        return redirect(
            "assessment_result",
            assessment_id=assessment.id
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
    
    # Calculate remaining time (timezone aware)
    now = timezone.now()
    remaining_seconds = 0
    if assessment.end_time:
        remaining_seconds = int((assessment.end_time - now).total_seconds())

    # If remaining time <= 0, immediately trigger auto-submission
    if remaining_seconds <= 0:
        trigger_auto_submit(request, assessment, task_ids, task, request.POST.get("answer", "").strip())
        return redirect(
            "assessment_result",
            assessment_id=assessment.id
        )

    estimated_time = request.session.get(f"task_{task.id}_time", "15 mins")

    # Handle answer
    if request.method == "POST":
        answer = request.POST.get(
            "answer",
            ""
        ).strip()
        print(f"[Views Debug] POST request received for task_id={task.id}. Answer length={len(answer)}")

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
                    "error": "Please enter your answer.",
                    "remaining_seconds": max(0, remaining_seconds)
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
        else:
            existing_submission.answer = answer
            existing_submission.save()

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

    existing_submission = Submission.objects.filter(
        assessment=assessment,
        task=task
    ).first()

    return render(
        request,
        "core/assessment_question.html",
        {
            "assessment": assessment,
            "task": task,
            "question_number": question_number,
            "total_questions": 5,
            "estimated_time": estimated_time,
            "existing_answer": existing_submission.answer if existing_submission else "",
            "remaining_seconds": max(0, remaining_seconds)
        }
    )

@login_required
def auto_submit_assessment(request, assessment_id):
    from django.http import JsonResponse
    import json

    assessment = get_object_or_404(
        Assessment,
        id=assessment_id,
        user=request.user
    )

    if assessment.completed_at:
        return JsonResponse({"success": True, "redirect_url": reverse("assessment_result", args=[assessment.id])})

    task_ids = request.session.get(f"assessment_{assessment.id}_tasks")
    if not task_ids:
        # Fallback to DB tasks if session is empty
        task_ids = list(Task.objects.filter(skill=assessment.skill).values_list("id", flat=True)[:5])

    # Get current task and answer from POST if present
    current_task = None
    current_answer = ""
    if request.method == "POST":
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
                current_answer = data.get("answer", "").strip()
                current_task_id = data.get("task_id")
                if current_task_id:
                    current_task = Task.objects.filter(id=current_task_id).first()
            except Exception as e:
                print("Error parsing JSON body in auto_submit:", e)
        else:
            current_answer = request.POST.get("answer", "").strip()
            current_task_id = request.POST.get("task_id")
            if current_task_id:
                current_task = Task.objects.filter(id=current_task_id).first()

    trigger_auto_submit(request, assessment, task_ids, current_task, current_answer)
    
    return JsonResponse({"success": True, "redirect_url": reverse("assessment_result", args=[assessment.id])})

@login_required
def assessment_violation(request, assessment_id):
    from django.http import JsonResponse
    import json
    if request.method == "POST":
        assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
        if not assessment.completed_at:
            try:
                data = json.loads(request.body)
                reason = data.get("reason", "cheating")
            except:
                reason = "cheating"

            assessment.score = 0
            assessment.passed = False
            assessment.completed_at = timezone.now()
            assessment.violation_reason = reason
            assessment.integrity_score = 0
            
            audit_entry = {
                "timestamp": timezone.now().isoformat(),
                "type": "violation",
                "severity": "fatal",
                "message": reason,
                "duration": 0
            }
            if not isinstance(assessment.audit_trail, list):
                assessment.audit_trail = []
            assessment.audit_trail.append(audit_entry)
            
            assessment.save()
        return JsonResponse({"success": True, "redirect_url": reverse('assessment_result', args=[assessment.id])})
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def log_warning(request, assessment_id):
    import json
    from django.http import JsonResponse
    if request.method == "POST":
        assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
        if not assessment.completed_at:
            try:
                data = json.loads(request.body)
                event_type = data.get("event_type", "warning")
                message = data.get("message", "Warning")
                duration = data.get("duration", 0)
                deduction = data.get("deduction", 2)
                
                audit_entry = {
                    "timestamp": timezone.now().isoformat(),
                    "type": event_type,
                    "severity": "warning",
                    "message": message,
                    "duration": duration
                }
                
                if not isinstance(assessment.audit_trail, list):
                    assessment.audit_trail = []
                    
                assessment.audit_trail.append(audit_entry)
                assessment.integrity_score = max(0, assessment.integrity_score - deduction)
                assessment.save(update_fields=['audit_trail', 'integrity_score'])
                return JsonResponse({"success": True})
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def assessment_heartbeat(request, assessment_id):
    from django.http import JsonResponse
    if request.method == "POST":
        assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
        if not assessment.completed_at:
            assessment.last_heartbeat = timezone.now()
            assessment.save(update_fields=['last_heartbeat'])
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid request"}, status=400)

def run_evaluation_pipeline(request, assessment, submissions, submission_type="Manual Submission"):
    if assessment.completed_at:
        return

    from .ai import evaluate_assessment_batch

    assessment.submission_type = submission_type
    
    total_seconds = int((timezone.now() - assessment.start_time).total_seconds()) if assessment.start_time else 0
    max_seconds = assessment.skill.duration * 60
    if submission_type == "Auto Submitted (Time Expired)":
        assessment.time_taken = min(total_seconds, max_seconds)
    else:
        assessment.time_taken = total_seconds

    # Batch AI evaluation
    batch_result = evaluate_assessment_batch(assessment, submissions)

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
                "user": assessment.user,
                "skill": assessment.skill,
            }
        )

def trigger_auto_submit(request, assessment, task_ids, current_task=None, current_answer=""):
    if assessment.completed_at:
        return

    # 1. Save current question's answer if provided
    if current_task:
        existing_sub = Submission.objects.filter(assessment=assessment, task=current_task).first()
        if not existing_sub:
            Submission.objects.create(
                assessment=assessment,
                user=assessment.user,
                task=current_task,
                answer=current_answer
            )
        else:
            existing_sub.answer = current_answer
            existing_sub.save()

    # 2. Fill all remaining tasks with blank submissions
    for t_id in task_ids:
        t = Task.objects.filter(id=t_id).first()
        if t:
            existing = Submission.objects.filter(assessment=assessment, task=t).first()
            if not existing:
                Submission.objects.create(
                    assessment=assessment,
                    user=assessment.user,
                    task=t,
                    answer=""
                )

    # 3. Retrieve all submissions
    submissions = Submission.objects.filter(
        assessment=assessment
    ).select_related("task").order_by("submitted_at")

    # 4. Run evaluation pipeline
    try:
        run_evaluation_pipeline(request, assessment, submissions, submission_type="Auto Submitted (Time Expired)")
    except Exception as e:
        print("Auto evaluation pipeline error:", e)

    # Clean up session
    request.session.pop(
        f"assessment_{assessment.id}_tasks",
        None
    )
    request.session.modified = True

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

    from django.contrib import messages

    try:
        run_evaluation_pipeline(request, assessment, submissions, submission_type="Manual Submission")
    except Exception as e:
        print("AI batch evaluation error:", e)
        messages.error(request, "AI evaluation failed. Please try again later.")
        return redirect("dashboard")

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

    verification_url = request.build_absolute_uri(
        reverse(
            "verify_certificate",
            args=[certificate.id]
        )
    )
    qr_code_base64 = generate_qr_base64(verification_url)

    return render(
        request,
        "core/certificate.html",
        {
            "certificate": certificate,
            "profile": profile,
            "qr_code_base64": qr_code_base64
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
    
    verification_url = request.build_absolute_uri(
        reverse(
            "verify_certificate",
            args=[certificate.id]
        )
    )
    qr_code_base64 = generate_qr_base64(verification_url)

    return render(
        request,
        "core/certificate_white.html",
        {
            "certificate": certificate,
            "qr_code_base64": qr_code_base64,
            "verification_url": verification_url,
            "is_owner": False,
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
        "core/certificate_white.html"
    )

    verification_url = request.build_absolute_uri(
        reverse(
            "verify_certificate",
            args=[certificate.id]
        )
    )
    qr_code_base64 = generate_qr_base64(verification_url)

    html = template.render({
        "certificate": certificate,
        "qr_code_base64": qr_code_base64,
        "verification_url": verification_url,
        "is_owner": False,
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

def about(request):
    return render(request, "core/about.html")

import json
from django.http import JsonResponse
from .models import ContactMessage

def contact(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            ContactMessage.objects.create(
                name=data.get('name', ''),
                email=data.get('email', ''),
                subject=data.get('subject', ''),
                message=data.get('message', '')
            )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return render(request, "core/contact.html")

def wallet_guide(request):
    return render(request, "core/wallet_guide.html")

def how_it_works(request):
    return render(request, "core/how_it_works.html")

@login_required
def show_white_certificate(request, certificate_id):
    certificate = get_object_or_404(
        Certificate,
        id=certificate_id,
        user=request.user
    )
    verification_url = request.build_absolute_uri(
        reverse(
            "verify_certificate",
            args=[certificate.id]
        )
    )
    qr_code_base64 = generate_qr_base64(verification_url)
    
    return render(
        request,
        "core/certificate_white.html",
        {
            "certificate": certificate,
            "qr_code_base64": qr_code_base64,
            "verification_url": verification_url,
            "is_owner": True,
        }
    )

@login_required
def my_assessments(request):
    from django.core.paginator import Paginator
    
    search_query = request.GET.get("q", "").strip()
    filter_val = request.GET.get("filter", "all").strip()
    sort_val = request.GET.get("sort", "newest").strip()
    
    assessments = Assessment.objects.filter(user=request.user, completed_at__isnull=False)
    
    if search_query:
        assessments = assessments.filter(skill__name__icontains=search_query)
        
    if filter_val == "passed":
        assessments = assessments.filter(passed=True)
    elif filter_val == "failed":
        assessments = assessments.filter(passed=False, completed_at__isnull=False)
        
    if sort_val == "oldest":
        assessments = assessments.order_by("completed_at")
    elif sort_val == "highest":
        assessments = assessments.order_by("-score")
    elif sort_val == "lowest":
        assessments = assessments.order_by("score")
    else:
        # newest
        assessments = assessments.order_by("-completed_at")
        
    paginator = Paginator(assessments, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, "core/my_assessments.html", {
        "page_obj": page_obj,
        "search_query": search_query,
        "filter_val": filter_val,
        "sort_val": sort_val,
    })
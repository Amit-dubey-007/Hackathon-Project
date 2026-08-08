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

from .ai import (
    generate_assessment_tasks,
    evaluate_submission,
)


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
            "evaluate_assessment",
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

        evaluations = Evaluation.objects.filter(
            submission__assessment=assessment
        ).order_by(
            "created_at"
        )

        # Certificate currently requires ONE evaluation.
        # Use the final/overall evaluation record for now.
        final_evaluation = evaluations.last()
        

        Certificate.objects.get_or_create(
            user=request.user,
            skill=assessment.skill,
            
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

    return render(
        request,
        "core/certificate.html",
        {
            "certificate": certificate
        }
    )
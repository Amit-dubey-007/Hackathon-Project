from django.urls import path
from . import views


urlpatterns = [

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "skills/",
        views.skill_list,
        name="skill_list"
    ),

    path(
        "skills/<int:skill_id>/",
        views.skill_detail,
        name="skill_detail"
    ),

    path(
        "skills/<int:skill_id>/start/",
        views.start_assessment,
        name="start_assessment"
    ),

    path(
        "assessment/<int:assessment_id>/question/<int:question_number>/",
        views.assessment_question,
        name="assessment_question"
    ),

    path(
        "assessment/<int:assessment_id>/evaluate/",
        views.evaluate_assessment,
        name="evaluate_assessment"
    ),

    path(
        "assessment/<int:assessment_id>/result/",
        views.assessment_result,
        name="assessment_result"
    ),
]
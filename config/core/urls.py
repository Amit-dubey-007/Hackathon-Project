# Triggering URLconf reload
from django.urls import path
from . import views


urlpatterns = [

    path("",views.home,name="home"),

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
        "skills/<int:skill_id>/agreement/",
        views.integrity_agreement,
        name="integrity_agreement"
    ),

    path(
        "skills/<int:skill_id>/start/",
        views.start_assessment,
        name="start_assessment"
    ),

    path(
        "assessment/<int:assessment_id>/violation/",
        views.assessment_violation,
        name="assessment_violation"
    ),

    path(
        "assessment/<int:assessment_id>/warning/",
        views.log_warning,
        name="log_warning"
    ),

    path(
        "assessment/<int:assessment_id>/heartbeat/",
        views.assessment_heartbeat,
        name="assessment_heartbeat"
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
        "assessment/<int:assessment_id>/auto-submit/",
        views.auto_submit_assessment,
        name="auto_submit_assessment"
    ),

    path(
        "assessment/<int:assessment_id>/result/",
        views.assessment_result,
        name="assessment_result"
    ),

    path(
        "certificate/<int:certificate_id>/",
        views.certificate_detail,
        name="certificate_detail"
    ),
    path(
        "certificate/<int:certificate_id>/mint/",
        views.mint_certificate_view,
        name="mint_certificate",
    ),
    path(
        "save-wallet/",
        views.save_wallet,
        name="save_wallet"
    ),
    path(
        "verify/<int:certificate_id>/",
        views.verify_certificate,
        name="verify_certificate",
    ),
    path(
        "wallet/manual/",
        views.save_wallet_manual,
        name="save_wallet_manual",
    ),
    path(
        "certificate/<int:certificate_id>/download/",
        views.download_certificate,
        name="download_certificate",
    ),
    path(
        "skills/<int:skill_id>/loading/",
        views.loading_questions_view,
        name="loading_questions"
    ),
    path(
        "assessment/<int:assessment_id>/loading-evaluation/",
        views.loading_evaluation_view,
        name="loading_evaluation"
    ),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("wallet-guide/", views.wallet_guide, name="wallet_guide"),
    path("how-it-works/", views.how_it_works, name="how_it_works"),
    path("certificate/<int:certificate_id>/view/", views.show_white_certificate, name="show_white_certificate"),
]

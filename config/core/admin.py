
# Register your models here.
from django.contrib import admin
from .models import Skill, Task, Submission, Evaluation, Certificate,Assessment


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "passing_score")
    search_fields = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "skill", "difficulty", "max_score")
    list_filter = ("skill", "difficulty")
    search_fields = ("title",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "task", "submitted_at")
    list_filter = ("submitted_at",)


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("submission", "score", "integrity_score", "created_at")
    list_filter = ("score",)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "skill",
        "minted",
        "token_id",
        "transaction_hash",
    )
    list_filter = ("minted", "skill")

admin.site.register(Assessment)
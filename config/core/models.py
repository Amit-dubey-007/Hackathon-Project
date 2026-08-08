from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Skill(models.Model):
    name = models.CharField(max_length=100)

    description = models.TextField()

    passing_score = models.IntegerField(
        default=70
    )

    def __str__(self):
        return self.name


class Task(models.Model):

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    title = models.CharField(
        max_length=500
    )

    question = models.TextField()

    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("Easy", "Easy"),
            ("Medium", "Medium"),
            ("Hard", "Hard"),
        ],
        default="Medium"
    )

    max_score = models.PositiveIntegerField(
        default=100
    )

    topic = models.CharField(
        max_length=300,
        blank=True
    )

    def __str__(self):
        return self.title


class Assessment(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE
    )

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    score = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    passed = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.user} - {self.skill}"


class Submission(models.Model):

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="submissions",
        blank=True,
        null=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE
    )

    answer = models.TextField()

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user} - {self.task}"


class Evaluation(models.Model):

    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE
    )

    score = models.PositiveIntegerField()

    feedback = models.TextField()

    strengths = models.TextField(
        blank=True
    )

    weaknesses = models.TextField(
        blank=True
    )

    suggestions = models.TextField(
        blank=True
    )

    integrity_score = models.PositiveIntegerField(
        default=100
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.submission.user} - {self.score}"


class Certificate(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE
    )

    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    token_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    transaction_hash = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    wallet_address = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    minted = models.BooleanField(
        default=False
    )

    issued_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user} - {self.skill}"
    
    
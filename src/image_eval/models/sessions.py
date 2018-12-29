import datetime
from hashlib import md5

from django.contrib import admin
from django.db import models
from django.db.models import QuerySet
from django.shortcuts import redirect

from .questions import Evaluation, Question


class Session(models.Model):
    hash = models.CharField(unique=True, max_length=32)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    comment = models.CharField(max_length=10_000)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)

    @staticmethod
    def create_new(evaluation, user_name, comment):
        created_at = datetime.datetime.now()
        md5_hash = md5(f'{evaluation.id} {user_name} {created_at}'.encode()).hexdigest()

        return Session(
            hash=md5_hash,
            evaluation=evaluation,
            user_name=user_name,
            comment=comment,
            created_at=created_at
        )

    @property
    def completed(self) -> bool:
        return self.completed_at is not None

    def complete(self) -> 'Session':
        self.completed_at = datetime.datetime.now()
        return self


class Assignment(models.Model):
    session = models.ForeignKey(Session, models.CASCADE, null=False)
    question = models.ForeignKey(Question, models.CASCADE, null=False)
    answer = models.IntegerField(null=False)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_name', 'evaluation', 'comment', 'created_at', 'completed_at']
    list_filter = ['evaluation']
    ordering = ['created_at']

__all__ = ['Session', 'Assignment']

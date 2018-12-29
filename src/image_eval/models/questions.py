import json

from django.db import models
from django.contrib import admin
from django.db.models import QuerySet
from django.shortcuts import redirect


class Evaluation(models.Model):
    TYPES = {
        'SEL': 'Image selection',
        'CLS': 'Image classification'
    }

    title = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    type = models.CharField(max_length=10, choices=TYPES.items())
    total_questions = models.IntegerField()

    def __str__(self):
        return f'{self.title} ({Evaluation.TYPES[self.type]})'


class Question(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    order = models.IntegerField()


class ImageClassificationQuestion(Question):
    image = models.ImageField()
    answers = models.TextField()

    @property
    def choices(self):
        parsed_answers = json.loads(self.answers)
        return list(zip(range(len(parsed_answers)), parsed_answers))


class ImageSelectionQuestion(Question):
    left_image = models.ImageField()
    right_image = models.ImageField()


class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_at', 'type', 'total_questions']
    ordering = ['created_at']

    actions = ['export_result']

    def export_result(self, request, queryset: QuerySet):
        return redirect('export_result', id=queryset.all()[0].id)


admin.site.register(Evaluation, EvaluationAdmin)

__all__ = ['Evaluation', 'Question', 'ImageSelectionQuestion', 'ImageClassificationQuestion']

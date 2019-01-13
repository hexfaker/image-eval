import json
import os
from typing import Iterable
from zipfile import ZipFile

import yaml
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.contrib import admin
from django.db.models import QuerySet
from django.forms import ModelForm, FileField, CharField
from django.shortcuts import redirect
from django.utils import timezone


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
    """
    Example:
          ::
        ImageSelectionQuestion(
            evaluation=e,
            text='Test test',
            order=0,
            left_image=ContentFile(b1, 'li0.png'),
            right_image=ContentFile(b2, 'ri0.png')
        ).save()

    """
    left_image = models.ImageField()
    right_image = models.ImageField()


class EvaluationForm(ModelForm):
    images = FileField()
    question = CharField(max_length=1000)


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    class InvalidZip(Exception):
        pass

    list_display = ['id', 'title', 'type', 'total_questions', 'created_at']
    ordering = ['created_at']
    actions = ['export_result']
    readonly_fields = ['created_at', 'total_questions']
    list_editable = ['title']
    list_display_links = None
    form = EvaluationForm

    def export_result(self, request, queryset: QuerySet):
        return redirect('export_result', id=queryset.all()[0].id)

    @transaction.atomic
    def save_model(self, request, obj, form: ModelForm, change):
        if change:
            super().save_model(request, obj, form, True)
        else:
            data = form.cleaned_data
            evaluation: Evaluation = Evaluation(title=data['title'],
                                                type=data['type'],
                                                created_at=timezone.now(),
                                                total_questions=0)
            evaluation.save()

            if data['type'] == 'SEL':
                zip_parser = self.make_selection_questions_from_zip
            else:
                zip_parser = self.make_classification_questions_from_zip

            evaluation.total_questions = zip_parser(
                data['images'],
                data['question'],
                evaluation
            )

            evaluation.save()

    @staticmethod
    def make_selection_questions_from_zip(zip_file_stream, question_text, evaluation):
        try:
            with ZipFile(zip_file_stream) as images:
                total_questions = EvaluationAdmin.get_total_questions(images.namelist(), 'left')

                if total_questions == 0:
                    raise Exception()

                questions = []
                for no in range(total_questions):
                    left_image_bytes = images.read(f'left/{no}.jpg')
                    right_image_bytes = images.read(f'right/{no}.jpg')

                    q = ImageSelectionQuestion(
                        evaluation=evaluation, text=question_text,
                        order=no,
                        left_image=ContentFile(left_image_bytes, f'{evaluation.id}_{no}_l.jpg'),
                        right_image=ContentFile(right_image_bytes, f'{evaluation.id}_{no}_r.jpg')
                    )
                    q.save()
                    questions.append(q)
            return total_questions
        except Exception:
            raise Exception('Zip parsing failed. Most likely the structure is wrong')

    @staticmethod
    def get_total_questions(fnames, prefix):
        total_questions = 0
        left_image_names: Iterable[str] = \
            filter(lambda s: s.startswith(prefix), fnames)

        for name in left_image_names:
            fname = name.split('/')[1]

            if len(fname) != 0:
                no = int(os.path.splitext(fname)[0]) + 1

                if no > total_questions:
                    total_questions = no

        return total_questions

    @staticmethod
    def make_classification_questions_from_zip(zip_file_stream, question_text, evaluation):
        try:
            with ZipFile(zip_file_stream) as images:
                total_questions = EvaluationAdmin.get_total_questions(images.namelist(), 'images')

                with images.open('answers.yml') as yml_stream:
                    answers = json.dumps(yaml.load(yml_stream))

                if total_questions == 0:
                    raise Exception()

                questions = []
                for no in range(total_questions):
                    image_bytes = images.read(f'images/{no}.jpg')

                    q = ImageClassificationQuestion(
                        evaluation=evaluation, text=question_text,
                        order=no,
                        answers=answers,
                        image=ContentFile(image_bytes, f'{evaluation.id}_{no}.jpg'),
                    )
                    q.save()
                    questions.append(q)
            return total_questions
        except Exception:
            raise Exception('Zip parsing failed. Most likely the structure is wrong')


__all__ = ['Evaluation', 'Question', 'ImageSelectionQuestion', 'ImageClassificationQuestion']

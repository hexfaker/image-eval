import hashlib
import json
from typing import List
from zipfile import ZipFile

import yaml
from django.contrib import admin
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models import QuerySet
from django.forms import ModelForm, FileField, CharField
from django.shortcuts import redirect
from django.utils import timezone
from model_utils.managers import InheritanceManager


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
    objects = InheritanceManager()

    def get_real_answer(self, answer):
        raise NotImplemented()


class ImageClassificationQuestion(Question):
    image = models.ImageField()
    answers = models.TextField()

    @property
    def choices(self):
        parsed_answers = json.loads(self.answers)
        return list(zip(range(len(parsed_answers)), parsed_answers))

    def get_real_answer(self, answer):
        return answer


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

    def _neeed_flip(self):
        hash = int(hashlib.sha1(f"{self.id}".encode()).hexdigest(), 16)
        return hash % 2 == 0

    def get_left_image(self):
        if self._neeed_flip():
            return self.right_image
        else:
            return self.left_image

    def get_right_image(self):
        if self._neeed_flip():
            return self.left_image
        else:
            return self.right_image

    def get_real_answer(self, answer):
        if self._neeed_flip():
            return 1 - answer
        return answer


class EvaluationForm(ModelForm):
    images = FileField()
    question = CharField(max_length=1000)


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
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
                baseline_images = EvaluationAdmin.get_fnames_with_prefix(
                    images, 'baseline/'
                )
                proposed_images = EvaluationAdmin.get_fnames_with_prefix(
                    images, 'proposed/'
                )

                # Remove all prefixes and exts to match names
                # proposed/first.jpg -> first
                baseline_image_names = {
                    name.rsplit('/', 1)[1].rsplit('.', 1)[0] for name in baseline_images
                }
                proposed_image_names = {
                    name.rsplit('/', 1)[1].rsplit('.', 1)[0] for name in proposed_images
                }

                if baseline_image_names != proposed_image_names:
                    raise Exception(
                        "Proposed and baseline image sets doesn't match"
                    )

                image_names = baseline_image_names

                total_questions = len(image_names)

                if total_questions == 0:
                    raise Exception("There must be at least one question")

                questions = []
                for no, name in enumerate(sorted(image_names)):
                    # Get image bytes without knowing extension
                    baseline_bytes = images.read(
                        EvaluationAdmin.get_fnames_with_prefix(images, f'baseline/{name}')[0]
                    )
                    proposed_bytes = images.read(
                        EvaluationAdmin.get_fnames_with_prefix(images, f'proposed/{name}')[0]
                    )

                    q = ImageSelectionQuestion(
                        evaluation=evaluation, text=question_text,
                        order=no,
                        left_image=ContentFile(baseline_bytes, f'{evaluation.id}_{no}_l.jpg'),
                        right_image=ContentFile(proposed_bytes, f'{evaluation.id}_{no}_r.jpg')
                    )
                    q.save()
                    questions.append(q)
            return total_questions
        except Exception as e:
            raise Exception('Zip parsing failed. Most likely the structure is wrong') from e

    @staticmethod
    def get_fnames_with_prefix(zip: ZipFile, prefix: str) -> List[str]:
        filenames = [item.filename for item in zip.filelist]
        return [name for name in filenames if name.startswith(prefix) and len(name) > len(prefix)]

    @staticmethod
    def make_classification_questions_from_zip(zip_file_stream, question_text, evaluation):
        try:
            with ZipFile(zip_file_stream) as images:
                image_names = EvaluationAdmin.get_fnames_with_prefix(
                    images, 'images/'
                )

                with images.open('answers.yml') as yml_stream:
                    answers = json.dumps(yaml.load(yml_stream))

                total_questions = len(image_names)
                if total_questions == 0:
                    raise Exception("There must be at least one question")

                questions = []
                for no, name in enumerate(image_names):
                    image_bytes = images.read(name)

                    q = ImageClassificationQuestion(
                        evaluation=evaluation, text=question_text,
                        order=no,
                        answers=answers,
                        image=ContentFile(image_bytes, f'{evaluation.id}_{no}.jpg'),
                    )
                    q.save()
                    questions.append(q)
            return total_questions
        except Exception as e:
            raise Exception('Zip parsing failed. Most likely the structure is wrong') from e


__all__ = ['Evaluation', 'Question', 'ImageSelectionQuestion', 'ImageClassificationQuestion']

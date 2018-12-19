import datetime
from hashlib import md5

from django.db import models


class Evaluation(models.Model):
    TYPES = (
        ('SEL', 'Image selection'),
        ('CLS', 'Image classification')
    )

    title = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    type = models.CharField(max_length=10, choices=TYPES)
    total_questions = models.IntegerField()


class Question(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    order = models.IntegerField()


class ImageClassificationQuestion(Question):
    image = models.ImageField()
    answers = models.TextField()


class ImageSelectionQuestion(Question):
    left_image = models.ImageField()
    right_image = models.ImageField()


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
        md5_hash = md5(f'{evaluation.id} {user_name} { created_at }'.encode()).hexdigest()

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

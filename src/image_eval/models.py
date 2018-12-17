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

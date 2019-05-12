import json
from io import BytesIO

from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image

from ..models import *

from django.contrib.auth import get_user_model

# see ref. below
UserModel = get_user_model()

if not UserModel.objects.filter(username='a').exists():
    user=UserModel.objects.create_user('a', password='a')
    user.is_superuser=True
    user.is_staff=True
    user.save()


def populate():
    e = Evaluation(title='Test', created_at=timezone.now(), type='SEL', total_questions=2)
    e.save()

    i1 = Image.new('RGB', (640, 1200), (255, 0, 0))
    i2 = Image.new('RGB', (640, 1200), (0, 255, 0))

    b1 = to_bytes(i1)
    b2 = to_bytes(i2)

    ImageSelectionQuestion(
        evaluation=e,
        text='Test test',
        order=0,
        left_image=ContentFile(b1, 'li0.png'),
        right_image=ContentFile(b2, 'ri0.png')
    ).save()

    ImageSelectionQuestion(
        evaluation=e,
        text='Test test1',
        order=1,
        left_image=ContentFile(b2, 'li1.png'),
        right_image=ContentFile(b1, 'ri1.png')
    ).save()

    e2 = Evaluation(title='Models 1', created_at=timezone.now(), type='CLS', total_questions=3)
    e2.save()

    answers = json.dumps(['Class 1', 'Class 2'])

    ImageClassificationQuestion(
        evaluation=e2,
        text='Select image class',
        answers=answers,
        order=0,
        image=ContentFile(b1, 'i0.png')
    ).save()

    ImageClassificationQuestion(
        evaluation=e2,
        text='Select image class',
        order=1,
        answers=answers,
        image=ContentFile(b2, 'i1.png')
    ).save()

    ImageClassificationQuestion(
        evaluation=e2,
        text='Select image class',
        answers=answers,
        order=2,
        image=ContentFile(b1, 'i2.png')
    ).save()


def to_bytes(image: Image.Image):
    stream = BytesIO()
    image.save(stream, 'JPEG')
    return stream.getvalue()

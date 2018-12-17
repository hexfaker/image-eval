from io import BytesIO

from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image

from ..models import *


def populate():
    e = Evaluation(title='Test', created_at=timezone.now(), type='SEL', total_questions=2)
    e.save()

    i1 = Image.new('RGB', (640, 480), (255, 0, 0))
    i2 = Image.new('RGB', (640, 480), (0, 255, 0))

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


def to_bytes(image: Image.Image):
    stream = BytesIO()
    image.save(stream, 'JPEG')
    return stream.getvalue()

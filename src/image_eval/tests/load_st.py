import json
from datetime import datetime
from pathlib import Path
from hashlib import md5

from django.core.files.base import ContentFile

from ..models import Evaluation, ImageSelectionQuestion, ImageClassificationQuestion


def load():
    IMAGE_PATH = 'tmp/site-eval'

    images = Path(IMAGE_PATH)

    image_prefixes = [i.name.replace('_noedges.jpg', '') for i in images.glob('*_noedges.jpg')]

    print(len(image_prefixes))

    e = Evaluation(title='Edge-aware vs Baseline', type='SEL', total_questions=len(image_prefixes),
                   created_at=datetime.now())
    e.save()

    info = {}

    for no, p in enumerate(image_prefixes):
        edges = (images / f'{p}_edges.jpg').read_bytes()
        noedges = (images / f'{p}_noedges.jpg').read_bytes()

        models = [edges, noedges]

        model_id = md5(p.encode()).digest()[-1] % 2

        info[p] = model_id

        ImageSelectionQuestion(
            evaluation=e,
            text='Select image you like more:',
            left_image=ContentFile(models[model_id], f'{p}_0.jpg'),
            right_image=ContentFile(models[1 - model_id], f'{p}_1.jpg'),
            order=no
        ).save()

    json.dump(info, open('site-eval-info.json', 'w'))

    e = Evaluation(title='Edge-aware rating', type='CLS', total_questions=len(image_prefixes),
                   created_at=datetime.now())
    e.save()
    answers = json.dumps([str(i) for i in range(1, 6)])

    for no, p in enumerate(image_prefixes):
        edges = (images / f'{p}_edges.jpg').read_bytes()

        ImageClassificationQuestion(
            evaluation=e,
            text='Rate image',
            image=ContentFile(edges, f'{p}_0.jpg'),
            answers=answers,
            order=no
        ).save()




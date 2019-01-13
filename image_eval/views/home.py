from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from image_eval.models import Evaluation


def home(request: HttpRequest, error=False):
    evaluations = Evaluation.objects.all()

    eval_info = {e.id: f'{e.title} ({Evaluation.TYPES[e.type]})' for e in evaluations}
    
    return render(request, 'home.html', dict(evaluations=eval_info, error=error))


__all__ = ['home']


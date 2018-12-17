from django.http import HttpRequest
from django.shortcuts import render

from ..models import ImageSelectionQuestion, Evaluation


def session_view(request: HttpRequest, id: str):
    return render(request, 'image_selection_question.html', dict(
        evaluation=Evaluation.objects.all()[0],
        question=ImageSelectionQuestion.objects.get(order=0),
        assignment_no=1
    ))


__all__ = ['session_view']

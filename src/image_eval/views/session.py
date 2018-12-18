from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import render, redirect

from ..models import Question, Evaluation, Session, Assignment, ImageSelectionQuestion


def session_view(request: HttpRequest, hash: str):
    session = Session.objects.get(hash=hash)

    if request.method == 'POST':
        question = Question.objects.get(id=int(request.POST['question_id']))
        answer = int(request.POST['answer'])

        next_order = question.order + 1
        
        ass = Assignment(question=question, session=session, answer=answer)
        ass.save()
    else:
        done_questions: QuerySet \
            = Assignment.objects.filter(session=session)\
            .order_by('-question__order')\
            .select_related('question')

        if done_questions.exists():
            next_order = done_questions[0].question.order + 1
        else:
            next_order = 0

    current_question = Question.objects.get(evaluation=session.evaluation, order=next_order)

    if hasattr(current_question, 'imageselectionquestion'):
        return render(request, 'image_selection_question.html', dict(
            question=current_question.imageselectionquestion,
            assignment_no=current_question.order + 1
        ))
    else:
        raise NotImplemented()


def new_session(request: HttpRequest):
    assert request.method == 'POST'

    session = Session.create_new(Evaluation.objects.all()[0], '', '')
    session.save()
    return redirect('session', hash=session.hash, permanent=True)


__all__ = ['session_view', 'new_session']

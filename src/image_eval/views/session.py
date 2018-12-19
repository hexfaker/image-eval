from django.db.models import QuerySet, Max
from django.http import HttpRequest
from django.shortcuts import render, redirect

from ..models import Question, Evaluation, Session, Assignment, ImageSelectionQuestion


def session_view(request: HttpRequest, hash: str):
    session = Session.objects.get(hash=hash)

    if not session.completed:
        if request.method == 'POST':
            question = Question.objects.get(id=int(request.POST['question_id']))
            answer = int(request.POST['answer'])

            next_order = question.order + 1

            ass = Assignment(question=question, session=session, answer=answer)
            ass.save()
        else:
            done_questions: QuerySet = Assignment.objects.filter(session=session)

            if done_questions.exists():
                next_order = done_questions.aggregate(Max('question__order'))['order__max'] + 1
            else:
                next_order = 0

        max_question_no = Question.objects \
            .filter(evaluation=session.evaluation) \
            .aggregate(Max('order'))['order__max']

        if max_question_no < next_order:
            session.complete().save()

    if session.completed:
        return render(request, 'session_completed.html')

    current_question = Question.objects.get(evaluation=session.evaluation, order=next_order)

    if hasattr(current_question, 'imageselectionquestion'):
        return render(request, 'image_selection_question.html', dict(
            question=current_question.imageselectionquestion,
            evaluation=session.evaluation,
        ))
    else:
        raise NotImplemented()


def new_session(request: HttpRequest):
    assert request.method == 'POST'

    evaluation_id = int(request.POST['evaluation_id'])
    comment = request.POST['comment']
    name = request.POST['name']

    session = Session.create_new(Evaluation.objects.get(id=evaluation_id), name, comment)
    session.save()
    return redirect('session', hash=session.hash, permanent=True)


__all__ = ['session_view', 'new_session']

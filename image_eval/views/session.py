import json

from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet, Max
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from .home import home
from ..models import Question, Evaluation, Session, Assignment


def render_question(request, session, question_no, error=False):
    current_question = Question.objects.get(evaluation=session.evaluation, order=question_no)

    if hasattr(current_question, 'imageselectionquestion'):

        return render(request, 'selection_question.html', dict(
            question=current_question.imageselectionquestion,
            evaluation=session.evaluation,
            error=error
        ))
    elif hasattr(current_question, 'imageclassificationquestion'):
        return render(request, 'classification_question.html', dict(
            question=current_question.imageclassificationquestion,
            evaluation=session.evaluation,
            error=error
        ))
    else:
        raise NotImplemented


def session_view(request: HttpRequest, hash: str):
    session = Session.objects.get(hash=hash)

    if not session.completed:
        if request.method == 'POST':
            question = Question.objects.get_subclass(id=int(request.POST['question_id']))

            if 'answer' not in request.POST:
                return render_question(request, session, question.order, True)

            raw_answer = request.POST['answer']
            answer = question.get_real_answer(int(raw_answer))

            next_order = question.order + 1

            ass = Assignment(question=question, session=session, answer=answer)
            ass.save()
        else:
            done_questions: QuerySet = Assignment.objects.filter(session=session)

            if done_questions.exists():
                query_res = done_questions.aggregate(Max('question__order'))
                next_order = query_res['question__order__max']
            else:
                next_order = 0

        max_question_no = Question.objects \
            .filter(evaluation=session.evaluation) \
            .aggregate(Max('order'))['order__max']

        if max_question_no < next_order:
            session.complete().save()

    if session.completed:
        return render(request, 'session_completed.html')

    return render_question(request, session, next_order)


def new_session(request: HttpRequest):
    assert request.method == 'POST'

    if len(request.POST['name']) == 0:
        return home(request, True)

    evaluation_id = int(request.POST['evaluation_id'])
    comment = request.POST['comment']
    name = request.POST['name']

    session = Session.create_new(Evaluation.objects.get(id=evaluation_id), name, comment)
    session.save()
    return redirect('session', hash=session.hash, permanent=True)


@login_required()
def export_results(request: HttpRequest, id: int):
    evaluation = Evaluation.objects.get(id=id)
    questions = Question.objects.filter(evaluation=evaluation)

    result = {}
    for q in questions:
        answers = [a.answer for a in
                   Assignment.objects.filter(question=q, session__completed_at__isnull=False)]
        result[q.order] = answers
    response = HttpResponse(content_type="application/json")
    json.dump(result, response)
    return response


__all__ = ['session_view', 'new_session', 'export_results']

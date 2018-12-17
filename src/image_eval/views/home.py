from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest):
    return render(request, 'home.html')


__all__ = ['home']


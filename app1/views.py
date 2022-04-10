from django.shortcuts import render
from . import violenceDetector


def home(request):
    return render(request, 'app1/index.html')


def detection(request):
    violenceDetector.detect()
    return render(request,'app1/index.html')

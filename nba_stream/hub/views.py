from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    return render(request, 'home.html', {'name' : 'from views py'})

def add2(request, a, b):
    c = int(a) + int(b)
    return HttpResponse(str(c))

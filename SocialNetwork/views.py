from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView
def home(request):
    user = request.user
    return render(request, 'main/home.html', {'user': user})
    return HttpResponse('Hello, world')

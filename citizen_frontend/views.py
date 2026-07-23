from django.shortcuts import render


def index(request):
    return render(request, "citizen_frontend/test.html")

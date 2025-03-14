from django.shortcuts import render

def home(request):
    return render(request, 'theme/home.html');
def Features(request):
    return render(request, 'theme/Features.html')
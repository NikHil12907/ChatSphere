from django.shortcuts import render

def home(request):
    return render(request, 'theme/home.html')
def Features(request):
    return render(request, 'theme/Features.html')
def privacy_policies(request):
    return render(request, 'theme/privacy_policy.html')
def terms_of_services(request):
    return render(request, 'theme/terms.html')
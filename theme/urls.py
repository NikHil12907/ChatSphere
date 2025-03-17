from django.urls import path
from .views import home, Features, privacy_policies, terms_of_services
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', home, name='home'),
    path('/Features', Features, name='Features'),
    path('/policies', privacy_policies, name='policies'),
    path('/terms', terms_of_services, name='terms'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete')
    
]


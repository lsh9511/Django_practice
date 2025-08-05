from django.contrib.auth.views import LogoutView
from django.urls import path

from homework.cb_views import SignupView, verify_email, LoginView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/', verify_email, name='verify_email'),
]
from django.urls import path
from panel import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginApp, name='login'),
    path('signup/', views.signupApp, name='signup'),
     path('reset_password/',
        auth_views.PasswordResetView.as_view(template_name="panel/password_reset.html"),
        name="reset_password"),
    path('reset_password_sent/',
        auth_views.PasswordResetDoneView.as_view(template_name="panel/password_reset_sent.html"),
        name="password_reset_done"),
    path('reset_password/<uidb64>/<token>',
        auth_views.PasswordResetConfirmView.as_view(template_name="panel/password_reset_confirm.html"),
        name="password_reset_confirm"),
    path('reset_password_complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name="panel/password_reset_done.html"),
        name="password_reset_complete"),
    path('logout/', views.logoutApp, name='logout'),
    path('wallet/', views.wallet_view, name='wallet_view'),
    path('add_deal/', views.add_deal, name='add_deal')
]

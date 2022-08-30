from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
    )
from django.urls import path, include
from mainapp.views import LandingPageView, SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('leads/', include('mainapp.urls', namespace='leads')),
    path('agents/', include('agents.urls', namespace='agents')),
    path('', LandingPageView.as_view(), name='landing_page'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('reset_password/', PasswordResetView.as_view(), name='reset_password'),
    path('password_reset_done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('password_reset_complete', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
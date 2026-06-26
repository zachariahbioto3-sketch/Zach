from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('preview/<slug:slug>/', views.preview, name='preview'),
]

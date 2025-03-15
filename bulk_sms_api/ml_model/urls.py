from django.urls import path
from . import views

urlpatterns = [
    path('run_model/', views.run_model, name='run_model'),
]
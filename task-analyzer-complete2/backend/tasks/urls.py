from django.urls import path
from . import views
urlpatterns = [
    path('analyze/', views.analyze, name='analyze'),
    path('suggest/', views.suggest, name='suggest'),
    path('feedback/', views.feedback, name='feedback'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('parse/', views.parse_view, name='parse_selenium'),
]


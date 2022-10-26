from django.urls import path
from . import views

urlpatterns=[
    path('palyer/',views.index)
]
from django.urls import path
from . import views

urlpatterns=[
    path('',views.player,name='player'),
    path('<word>/',views.get_player,name='get_player'),
]
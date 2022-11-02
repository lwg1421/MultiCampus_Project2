from django.urls import path
from . import views

urlpatterns=[
    path('',views.player,name='player'),
    # 선수 이름으로 url이 갈려서 페이지 표시하고 싶음
    path('<str:word>/',views.get_player,name='get_player'),
]
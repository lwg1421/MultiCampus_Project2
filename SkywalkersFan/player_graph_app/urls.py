from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns=[
    path('',views.player,name='player'),
    # 선수 이름으로 url이 갈려서 페이지 표시하고 싶음
    path('<str:word>/',views.get_player,name='get_player'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
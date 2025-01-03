from django.urls import path 
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('add', views.add, name='add_video'),
    path('video_list', views.video_list, name='video_list'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail')
]
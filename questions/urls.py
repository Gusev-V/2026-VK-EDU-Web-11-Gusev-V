from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ask/', views.ask, name='ask'),
    path('tag/<str:tag_name>/', views.tags, name='tags'),
    path('question/<int:question_id>/', views.question, name='question'),
]
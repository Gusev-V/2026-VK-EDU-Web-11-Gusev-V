from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ask/', views.ask, name='ask'),
    path('tag/<str:tag_name>/', views.tags, name='tags'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('search/', views.search_redirect, name='search_redirect'),

    path('ajax/like-question/', views.like_question, name='like_question'),
    path('ajax/like-answer/', views.like_answer, name='like_answer'),
    path('ajax/mark-correct/', views.mark_correct, name='mark_correct'),
]
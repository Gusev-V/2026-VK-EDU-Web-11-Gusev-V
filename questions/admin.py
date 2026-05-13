from django.contrib import admin
from .models import Tag, Question, Answer, QuestionLike, AnswerLike


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'content', 'author', 'likes_count', 'created_at', 'likes_count']
    search_fields = ['title', 'content']
    list_filter = ['tags', 'created_at']
    filter_horizontal = ['tags']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'content', 'author', 'is_correct', 'likes_count']
    list_filter = ['is_correct']
    search_fields = ['content', 'title']


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'created_at']


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'answer', 'created_at']
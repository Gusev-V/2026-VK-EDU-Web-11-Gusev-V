from django.db.models import Count
from questions.models import Tag
from django.contrib.auth.models import User


def sidebar(request):
    popular_tags = Tag.objects.annotate(
        questions_cnt=Count('questions')
    ).order_by('-questions_cnt')[:10]

    best_members = User.objects.annotate(
        total=Count('questions', distinct=True) + Count('answers', distinct=True)
    ).filter(
        total__gt=0
    ).select_related('profile').order_by('-total')[:10]

    return {
        'popular_tags': popular_tags,
        'best_members': best_members,
    }


def current_user_info(request):

    return {
    }

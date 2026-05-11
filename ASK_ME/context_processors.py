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
    # username = 'Dr. Pepper'
    # user_icon = 'img/user-icon.svg'
    # user_email = 'dr.pepper-+@@@mail.ru'
    # login = 'dr_pepper'
    #
    # excluded_urls = ['login', 'registration']
    #
    # if request.resolver_match and request.resolver_match.url_name in excluded_urls:
    #     return {}

    return {
        # 'current_user_info': {
        #     'username': username,
        #     'icon': user_icon,
        #     'login': login,
        #     'email': user_email,
        # }
    }

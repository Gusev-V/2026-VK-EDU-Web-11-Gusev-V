def sidebar(request):
    popular_tags = ['perl', 'python', 'MySQL', 'django', 'Mail.ru', 'Voloshin', 'Firefox']
    best_members = ['Mr.Freeman', 'Dr.House', 'Bender', 'Queen Victoria', 'V.Pupkin']
    return {
        'popular_tags': popular_tags,
        'best_members': best_members,
    }


def user(request):
    username = 'Dr. Pepper'
    user_icon = 'img/user-icon.svg'
    user_email = 'dr.pepper-+@@@mail.ru'
    login = 'dr_pepper'

    excluded_urls = ['login', 'registration']

    if request.resolver_match and request.resolver_match.url_name in excluded_urls:
        return {}

    return {
        'user': {
            'username': username,
            'icon': user_icon,
            'login': login,
            'email': user_email,
        }
    }

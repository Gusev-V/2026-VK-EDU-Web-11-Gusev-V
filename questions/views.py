from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)

    page_number = request.GET.get('page', 1)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page


def index(request):
    questions = []
    for i in range(100):
        questions.append({
            'id': i,
            'title': f'How to build a moon park?_{i}',
            'text': "Guys, I have trouble with a moon park. Can't find the black-jack...",
            'votes': 5,
            'answers_count': 50,
            'tags': ['black-jack', 'bender'],
            'avatar': f'img/user-icon.svg',
        })

    page = paginate(questions, request, 5)
    context = {
        'page_obj': page,
    }
    return render(request, 'questions/index.html', context)


def ask(request):
    return render(request, 'questions/ask.html')


def tags(request, tag_name):
    questions = []
    for i in range(100):
        questions.append({
            'id': i,
            'title': f'How to build a moon park?_{i}',
            'text': "Guys, I have trouble with a moon park. Can't find the black-jack...",
            'votes': 5,
            'answers_count': 3,
            'tags': ['black-jack', 'bender'],
            'avatar': f'img/user-icon.svg',
        })

    page = paginate(questions, request, per_page=5)

    context = {
        'page_obj': page,
        'tag_name': tag_name,
    }
    return render(request, 'questions/tags.html', context)


def question(request, question_id):

    question_data = {
        'title': 'How to build a moon park?',
        'text': "Lorem ipsum - dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt"
                " ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci "
                "tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.",
        'votes': 5,
        'answers_count': 3,
        'tags': ['black-jack', 'bender'],
        'avatar': f'img/user-icon.svg',
        'id': question_id
    }

    answers = []
    for i in range(50):
        answers.append({
            'title': f'How to build a moon park?_{i}',
            'text': "First of all I would like to thank you for the invitation to participate in such a... Russia is"
                    " the huge territory which in many respects needs to be render habitable.",
            'votes': 5,
            'is_correct': i % 2,
            'avatar': 'img/user-icon.svg',
        })

    page = paginate(answers, request, per_page=3)

    context = {
        'page_obj': page,
        'question': question_data,
    }

    return render(request, 'questions/question.html', context)

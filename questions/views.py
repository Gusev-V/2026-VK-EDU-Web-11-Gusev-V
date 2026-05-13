from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from questions.models import Question, Answer, QuestionLike, Tag


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
    questions = Question.objects.get_hot_questions()
    page = paginate(questions, request, 5)
    context = {
        'page_obj': page,
        'empty_message': 'No questions yet. Be the first to ask!',
    }
    return render(request, 'questions/index.html', context)


def ask(request):
    return render(request, 'questions/ask.html')


def tags(request, tag_name):
    tag_name = tag_name.lower()
    questions = Question.objects.get_questions_by_tag(tag_name)

    if not questions.exists():
        get_object_or_404(Tag, name=tag_name)

    page = paginate(questions, request, per_page=20)

    context = {
        'page_obj': page,
        'tag_name': tag_name,
        'empty_message': f'No questions found for tag "{tag_name}".',
    }
    return render(request, 'questions/tags.html', context)


def question(request, question_id):
    question_obj = get_object_or_404(
        Question.objects.select_related('author__profile').prefetch_related('tags'),
        pk=question_id
    )

    answers = Answer.objects.filter(question=question_obj).select_related(
        'author__profile'
    ).annotate(
        ans_likes=Count('answer_likes', distinct=True)
    ).order_by('-is_correct', '-ans_likes', '-created_at')

    page = paginate(answers, request, per_page=10)

    question_likes = QuestionLike.objects.filter(question=question_obj).count()

    context = {
        'question': question_obj,
        'question_likes': question_likes,
        'page_obj': page,
        'empty_message': 'No answers yet. Be the first to answer this question!',
    }
    return render(request, 'questions/question.html', context)

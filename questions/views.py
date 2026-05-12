from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from questions.models import Question, Answer, QuestionLike, Tag
from .forms import QuestionForm, AnswerForm


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
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            tag_names = form.cleaned_data.get('tags', [])
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)
            return redirect('question', question_id=question.id)
    else:
        form = QuestionForm()

    context = {
        'form': form,
    }

    return render(request, 'questions/ask.html', context)


def tags(request, tag_name):
    tag_name = tag_name.lower()
    questions = Question.objects.get_questions_by_tag(tag_name)

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

    answer_form = AnswerForm()

    if request.method == 'POST' and request.user.is_authenticated:
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.question = question_obj
            answer.author = request.user
            answer.save()
            return redirect(f'/question/{question_id}')

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
        'answer_form': answer_form,
        'empty_message': 'No answers yet. Be the first to answer this question!',
    }
    return render(request, 'questions/question.html', context)


def search_redirect(request):
    query = request.GET.get('q', '').strip().lower()
    if query:
        return redirect('tags', tag_name=query)
    return redirect('index')
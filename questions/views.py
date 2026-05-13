from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Question, Answer, QuestionLike, Tag, AnswerLike
from .forms import QuestionForm, AnswerForm
import json


@login_required
@require_POST
def like_question(request):
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        action = data.get('action')

        if not question_id or action not in ['like', 'dislike']:
            return JsonResponse({'error': 'Invalid parameters'}, status=400)

        question = get_object_or_404(Question, pk=question_id)

        if action == 'like':
            if QuestionLike.objects.filter(user=request.user, question=question).exists():
                return JsonResponse({'error': 'Already liked'}, status=400)
            QuestionLike.objects.create(user=request.user, question=question)
        else:
            like = QuestionLike.objects.filter(user=request.user, question=question).first()
            if not like:
                return JsonResponse({'error': 'Nothing to dislike'}, status=400)
            like.delete()

        return JsonResponse({
            'status': 'ok',
            'likes_count': question.question_likes.count()
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required
@require_POST
def like_answer(request):
    try:
        data = json.loads(request.body)
        answer_id = data.get('answer_id')
        action = data.get('action')

        if not answer_id or action not in ['like', 'dislike']:
            return JsonResponse({'error': 'Invalid parameters'}, status=400)

        answer = get_object_or_404(Answer, pk=answer_id)

        if action == 'like':
            if AnswerLike.objects.filter(user=request.user, answer=answer).exists():
                return JsonResponse({'error': 'Already liked'}, status=400)
            AnswerLike.objects.create(user=request.user, answer=answer)
        else:
            like = AnswerLike.objects.filter(user=request.user, answer=answer).first()
            if not like:
                return JsonResponse({'error': 'Nothing to dislike'}, status=400)
            like.delete()

        return JsonResponse({
            'status': 'ok',
            'likes_count': answer.answer_likes.count()
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required
@require_POST
def mark_correct(request):
    try:
        data = json.loads(request.body)
        answer_id = data.get('answer_id')

        if not answer_id:
            return JsonResponse({'error': 'Invalid parameters'}, status=400)

        answer = get_object_or_404(Answer.objects.select_related('question'), pk=answer_id)

        if request.user != answer.question.author:
            return JsonResponse({'error': 'Only question author can mark correct answer'}, status=403)

        answer.is_correct = not answer.is_correct
        answer.save()

        return JsonResponse({
            'status': 'ok',
            'is_correct': answer.is_correct
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


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
    liked_questions = set()
    if request.user.is_authenticated:
        liked_questions = set(
            QuestionLike.objects.filter(
                user=request.user,
                question__in=questions
            ).values_list('question_id', flat=True)
        )

    page = paginate(questions, request, 5)
    context = {
        'page_obj': page,
        'empty_message': 'No questions yet. Be the first to ask!',
        'liked_questions': liked_questions,
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

    liked_questions = set()
    if request.user.is_authenticated:
        liked_questions = set(
            QuestionLike.objects.filter(
                user=request.user,
                question__in=questions
            ).values_list('question_id', flat=True)
        )

    page = paginate(questions, request, per_page=20)

    context = {
        'page_obj': page,
        'tag_name': tag_name,
        'empty_message': f'No questions found for tag "{tag_name}".',
        'liked_questions': liked_questions,

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

    question_liked = False
    liked_answers = set()

    if request.user.is_authenticated:
        question_liked = QuestionLike.objects.filter(
            user=request.user, question=question_obj
        ).exists()
        liked_answers = set(
            AnswerLike.objects.filter(
                user=request.user,
                answer__in=answers
            ).values_list('answer_id', flat=True)
        )

    context = {
        'question': question_obj,
        'question_liked': question_liked,
        'liked_answers': liked_answers,
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
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.core.exceptions import ValidationError


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def _optimize(self, queryset):
        return queryset.select_related(
            'author__profile'
        ).prefetch_related(
            'tags',
            'question_likes'
        ).annotate(
            answers_cnt=Count('answers', distinct=True)
        )

    def get_new_questions(self):
        queryset = self.get_queryset().order_by('-created_at')
        return self._optimize(queryset)

    def get_best_questions(self):
        queryset = self.get_queryset().annotate(
            likes_cnt=Count('question_likes')
        ).order_by('-likes_cnt', '-created_at')
        return self._optimize(queryset)

    def get_hot_questions(self):
        queryset = self.get_queryset().annotate(
            total_activity=Count('question_likes', distinct=True) +
                           Count('answers__answer_likes', distinct=True)
        ).order_by('-total_activity', '-created_at')
        return self._optimize(queryset)

    def get_questions_by_tag(self, tag_name):
        queryset = self.get_queryset().filter(
            tags__name=tag_name
        ).distinct()
        return self._optimize(queryset)


class Question(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Создатель вопроса'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    content = models.TextField(
        verbose_name='Текст вопроса'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='questions',
        verbose_name='Теги',
        blank=True
    )
    likes_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name='Количество лайков'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return self.title[:100]

    def update_likes_count(self):
        self.likes_count = self.question_likes.count()
        self.save(update_fields=['likes_count'])

    def get_answers(self):
        return self.answers.all()

    def get_correct_answer(self):
        return self.answers.filter(is_correct=True).first()


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Создатель ответа'
    )
    content = models.TextField(
        verbose_name='Текст ответа'
    )
    likes_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name='Количество лайков'
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name='Правильный ответ'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-is_correct', '-likes_count', '-created_at']

    def __str__(self):
        if self.content:
            return f'Ответ: {self.content[:50]}'
        return f'Ответ #{self.id} на "{self.question.content[:30]}"'

    def update_likes_count(self):
        self.likes_count = self.answer_likes.count()
        self.save(update_fields=['likes_count'])

    def clean(self):
        if self.is_correct and self.author != self.question.author:
            raise ValidationError({
                'is_correct': 'Только автор вопроса может отметить ответ как правильный.'
            })

    def save(self, *args, **kwargs):
        if self.pk:
            old_answer = Answer.objects.get(pk=self.pk)
            if not old_answer.is_correct and self.is_correct:

                if self.author != self.question.author:
                    raise ValidationError(
                        'Только автор вопроса может отметить ответ как правильный.'
                    )
        else:
            if self.is_correct and self.author != self.question.author:
                raise ValidationError(
                    'Только автор вопроса может отметить ответ как правильный.'
                )
        super().save(*args, **kwargs)


class QuestionLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='question_likes',
        verbose_name='Пользователь'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='question_likes',
        verbose_name='Вопрос'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата лайка'
    )

    class Meta:
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'
        unique_together = ['user', 'question']
        ordering = ['-created_at']

    def __str__(self):
        return f'Лайк вопроса от {self.user.username}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.question.update_likes_count()

    def delete(self, *args, **kwargs):
        question = self.question
        super().delete(*args, **kwargs)
        question.update_likes_count()


class AnswerLike(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answer_likes',
        verbose_name='Пользователь'
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='answer_likes',
        verbose_name='Ответ'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата лайка'
    )

    class Meta:
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
        unique_together = ['user', 'answer']
        ordering = ['-created_at']

    def __str__(self):
        return f'Лайк ответа #{self.answer.id} от {self.user.username}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.answer.update_likes_count()

    def delete(self, *args, **kwargs):
        answer = self.answer
        super().delete(*args, **kwargs)
        answer.update_likes_count()
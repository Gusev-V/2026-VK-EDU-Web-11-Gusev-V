import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from faker import Faker
from core.models import Profile
from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения данных')

    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker()
        Faker.seed(0)

        users_count = ratio
        questions_count = ratio * 10
        answers_count = ratio * 100
        tags_count = ratio
        likes_count = ratio * 200

        self.stdout.write(f'Начинаем заполнение базы данных (ratio={ratio}):')
        self.stdout.write(f'  Пользователей: {users_count}')
        self.stdout.write(f'  Вопросов: {questions_count}')
        self.stdout.write(f'  Ответов: {answers_count}')
        self.stdout.write(f'  Тегов: {tags_count}')
        self.stdout.write(f'  Лайков: {likes_count}')

        self.stdout.write('Создание пользователей')
        users = self.create_users(users_count, fake)

        self.stdout.write('Создание профилей')
        profiles = self.create_profiles(users, fake)

        self.stdout.write('Создание тегов')
        tags = self.create_tags(tags_count, fake)

        self.stdout.write('Создание вопросов')
        questions = self.create_questions(questions_count, users, tags, fake)

        self.stdout.write('Создание ответов')
        answers = self.create_answers(answers_count, questions, users, fake)

        self.stdout.write('Создание лайков')
        self.create_likes(likes_count, users, questions, answers)

        self.stdout.write(self.style.SUCCESS(f'База данных заполнена (ratio={ratio})'))


    def create_users(self, count, fake):
        """Создание пользователей с использованием bulk_create"""
        users = []
        for i in range(count):
            username = f'{fake.user_name()}_{i}'
            email = fake.email()
            password = 'password123'

            user = User(
                username=username,
                email=email,
                password='',
                date_joined=timezone.now() - timedelta(days=random.randint(0, 365))
            )
            users.append(user)

        User.objects.bulk_create(users, batch_size=1000)

        return User.objects.all().order_by('-id')[:count]

    def create_profiles(self, users, fake):
        """Создание профилей для пользователей"""
        profiles = []
        for user in users:
            profile = Profile(
                user=user,
                nickname=fake.user_name(),
            )
            profiles.append(profile)

        Profile.objects.bulk_create(profiles, batch_size=1000, ignore_conflicts=True)
        return Profile.objects.all().order_by('-id')[:len(users)]

    def create_tags(self, count, fake):
        """Создание тегов"""
        tags = []
        used_names = set()

        while len(tags) < count:
            name = fake.word()
            if len(name) > 100:
                name = name[:100]

            if name not in used_names:
                used_names.add(name)
                tag = Tag(name=name)
                tags.append(tag)

        Tag.objects.bulk_create(tags, batch_size=1000, ignore_conflicts=True)

        return Tag.objects.all().order_by('-id')[:count]

    def create_questions(self, count, users, tags, fake):
        """Создание вопросов"""
        questions = []
        users_list = list(users)
        tags_list = list(tags)

        for i in range(count):
            title = fake.sentence(nb_words=6).rstrip('.')
            content = '\n'.join(fake.paragraphs(nb=3))
            author = random.choice(users_list)

            question = Question(
                title=title,
                content=content,
                author=author,
                likes_count=0,
                created_at=timezone.now() - timedelta(
                    days=random.randint(0, 365),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
            )
            questions.append(question)

        Question.objects.bulk_create(questions, batch_size=1000)

        created_questions = Question.objects.all().order_by('-id')[:count]

        self.add_tags_to_questions(created_questions, tags_list)

        return created_questions

    def add_tags_to_questions(self, questions, tags_list):
        """Добавление тегов к вопросам через промежуточную таблицу"""
        ThroughModel = Question.tags.through
        through_objects = []

        for question in questions:
            num_tags = random.randint(1, min(5, len(tags_list)))
            selected_tags = random.sample(tags_list, num_tags)

            for tag in selected_tags:
                through_objects.append(
                    ThroughModel(
                        question_id=question.id,
                        tag_id=tag.id
                    )
                )

        ThroughModel.objects.bulk_create(through_objects, batch_size=1000, ignore_conflicts=True)

    def create_answers(self, count, questions, users, fake):
        """Создание ответов"""
        answers = []
        questions_list = list(questions)
        users_list = list(users)

        for i in range(count):
            question = random.choice(questions_list)
            author = random.choice(users_list)

            answer = Answer(
                question=question,
                author=author,
                content='\n'.join(fake.paragraphs(nb=2)),
                likes_count=0,
                is_correct=False,
                created_at=timezone.now() - timedelta(
                    days=random.randint(0, 365),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
            )
            answers.append(answer)

        Answer.objects.bulk_create(answers, batch_size=1000)

        created_answers = Answer.objects.all().order_by('-id')[:count]

        self.set_correct_answers(created_answers, questions_list)

        return created_answers

    def set_correct_answers(self, answers, questions):
        """Установка правильных ответов"""
        from collections import defaultdict
        answers_by_question = defaultdict(list)

        for answer in answers:
            answers_by_question[answer.question_id].append(answer)

        correct_answers = []
        for question_id, question_answers in answers_by_question.items():
            if question_answers:
                num_correct = random.randint(1, min(2, len(question_answers)))
                selected = random.sample(question_answers, num_correct)

                for answer in selected:
                    answer.is_correct = True
                    correct_answers.append(answer)

        Answer.objects.bulk_update(correct_answers, ['is_correct'], batch_size=1000)

    def create_likes(self, count, users, questions, answers):
        """Создание лайков для вопросов и ответов"""
        users_list = list(users)
        questions_list = list(questions)
        answers_list = list(answers)

        question_likes_count = int(count * 0.6)
        answer_likes_count = count - question_likes_count

        self.create_question_likes(question_likes_count, users_list, questions_list)

        self.create_answer_likes(answer_likes_count, users_list, answers_list)

        self.update_likes_counts(questions_list, answers_list)

    def create_question_likes(self, count, users, questions):
        """Создание лайков для вопросов"""
        likes = []
        used_combinations = set()

        attempts = 0
        max_attempts = count * 3

        while len(likes) < count and attempts < max_attempts:
            user = random.choice(users)
            question = random.choice(questions)

            combination = (user.id, question.id)
            if combination not in used_combinations:
                used_combinations.add(combination)
                likes.append(
                    QuestionLike(
                        user=user,
                        question=question,
                        created_at=timezone.now() - timedelta(
                            days=random.randint(0, 365)
                        )
                    )
                )

            attempts += 1

        QuestionLike.objects.bulk_create(likes, batch_size=1000, ignore_conflicts=True)

    def create_answer_likes(self, count, users, answers):
        """Создание лайков для ответов"""
        likes = []
        used_combinations = set()

        attempts = 0
        max_attempts = count * 3

        while len(likes) < count and attempts < max_attempts:
            user = random.choice(users)
            answer = random.choice(answers)

            combination = (user.id, answer.id)
            if combination not in used_combinations:
                used_combinations.add(combination)
                likes.append(
                    AnswerLike(
                        user=user,
                        answer=answer,
                        created_at=timezone.now() - timedelta(
                            days=random.randint(0, 365)
                        )
                    )
                )

            attempts += 1

        AnswerLike.objects.bulk_create(likes, batch_size=1000, ignore_conflicts=True)

    def update_likes_counts(self, questions, answers):
        for question in questions:
            question.likes_count = QuestionLike.objects.filter(question=question).count()

        Question.objects.bulk_update(
            questions, ['likes_count'], batch_size=1000
        )

        for answer in answers:
            answer.likes_count = AnswerLike.objects.filter(answer=answer).count()

        Answer.objects.bulk_update(
            answers, ['likes_count'], batch_size=1000
        )
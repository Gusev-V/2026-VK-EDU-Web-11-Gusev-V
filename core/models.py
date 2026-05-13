from django.db import models
from django.contrib.auth.models import User
import uuid
import os


def avatar_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    new_filename = f"{uuid.uuid4()}{ext}"
    return f'avatars/{new_filename}'


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    nickname = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Никнейм'
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        verbose_name='Аватарка'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        ordering = ['nickname']

    def __str__(self):
        return f'{self.nickname} ({self.user.username})'

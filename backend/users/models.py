import textwrap

from django.contrib.auth.models import AbstractUser
from django.db import models

TITLE_STR_MAX_LENGTH = 30


class User(AbstractUser):
    avatar = models.ImageField(
        upload_to="avatar/",
        blank=True,
        null=True,
        verbose_name="Аватар",
    )
    email = models.EmailField(unique=True)

    class Meta(AbstractUser.Meta):
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriber",
        verbose_name="Подписчик",
    )
    subscription = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribed_to",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return textwrap.shorten(
            f"{self.user.username} подписан на {self.subscription.username}",
            width=TITLE_STR_MAX_LENGTH,
            placeholder="...",
        )

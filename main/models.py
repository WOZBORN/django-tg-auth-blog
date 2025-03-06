from django.db import models

class TelegramUser(models.Model):
    tg_id = models.BigIntegerField(unique=True, verbose_name='Telegram ID')
    telegram_nickname = models.CharField(max_length=150, verbose_name='Ник в Telegram')
    register_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    token = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name='Токен для входа')

    def __str__(self):
        return f'{self.telegram_nickname} (ID: {self.tg_id})'


class Post(models.Model):
    author = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст поста')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    likes = models.PositiveIntegerField(default=0, verbose_name='Количество лайков')

    def __str__(self):
        return self.title

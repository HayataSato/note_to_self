from django.db import models
from django.utils import timezone

from markdownx.models import MarkdownxField


class Category(models.Model):
    """タスクのカテゴリ"""
    name = models.CharField(default="", max_length=20)

    def __str__(self):
        return self.name


class Task(models.Model):
    """タスク(名前，カテゴリ,優先度，取り組んだ時間，登録日時,ステータス)"""
    name = models.CharField(default="", max_length=100, blank=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True)
    pri = models.IntegerField(blank=False, null=False, default=0)
    time = models.CharField(default="00:00", max_length=100, blank=False)
    rgst = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Summary(models.Model):
    """ まとめ(子モデル) """
    task = models.ForeignKey(Task, verbose_name='task', related_name='summaries', on_delete=models.CASCADE)
    title = models.CharField(default="", max_length=100, blank=False)
    summary = MarkdownxField('', help_text='Markdown形式で書いてください。')
    rgst = models.DateTimeField(default=timezone.now)
    updt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.summary


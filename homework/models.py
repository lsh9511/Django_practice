from django.contrib.auth import get_user_model
from django.db import models

from utils.models import TimestampModel

# Create your models here.

User = get_user_model()

class Todo(TimestampModel):
    title = models.CharField('제목',max_length=50)
    description = models.TextField('설명')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField('시작일')
    end_date = models.DateField('마감일',)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '할 일'
        verbose_name_plural = '할 일 리스트'


class Comment(TimestampModel):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=200)

    def __str__(self):
        return self.message[5]

    class Meta:
        verbose_name = '댓글'
        verbose_name_plural = '댓글 목록'

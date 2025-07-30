from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.

User = get_user_model()

class Todo(models.Model):
    title = models.CharField('제목',max_length=50)
    description = models.TextField('설명')
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField('시작일')
    end_date = models.DateField('마감일',)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

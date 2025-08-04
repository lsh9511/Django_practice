from io import BytesIO

from django.contrib.auth import get_user_model
from django.db import models
from PIL import Image
from pathlib import Path

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
    completed_image = models.ImageField('완료이미지', upload_to='images/%Y/%m/%d', null=True, blank=True)
    thumbnail = models.ImageField('썸네일',upload_to='images/%Y/%m/%d/thumbnail', null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.completed_image:
            return super().save(*args,**kwargs)

        image = Image.open(self.completed_image)
        image.thumbnail((300,300))

        image_path = Path(self.completed_image.name)

        thumbnail_name = image_path.stem
        thumbnail_extension = image_path.suffix.lower()
        thumbnail_filename = f'{thumbnail_name}_thumb{thumbnail_extension}'

        if thumbnail_extension in ['.jpg','.jpeg'] :
            file_type = 'JPEG'
        elif thumbnail_extension == '.gif':
            file_type = 'GIF'
        elif thumbnail_extension == '.png':
            file_type = 'PNG'
        else:
            return super().save(*args,**kwargs)

        temp_thumb = BytesIO()
        image.save(temp_thumb, file_type)
        temp_thumb.seek(0)

        self.thumbnail.save(thumbnail_filename,temp_thumb, save=False)
        temp_thumb.close()
        return super().save(*args,**kwargs)


    def get_thumbnail_image_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        elif self.completed_image:
            return self.completed_image.url
        return None



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

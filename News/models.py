import os.path
import textwrap
import uuid
from datetime import datetime
from io import BytesIO

from PIL import Image
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="posts")
    importance = models.SmallIntegerField(default=0)
    publishDate = models.DateTimeField(default=datetime.now)
    image = models.ImageField()
    article = RichTextField()
    visits = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.id}, " \
               f"{textwrap.shorten(self.title, width=50, placeholder='...')}, " \
               f"{self.publishDate.strftime('%Y-%m-%d %H:%M:%S')}, " \
               f"{self.author.last_name}, {self.author.first_name}"

    def save(self, *args, **kwargs):
        # Resize and convert image
        im = Image.open(self.image)
        im = im.resize((640, int(im.height * 640 / im.width)), Image.LANCZOS)
        out = BytesIO()
        im.save(out, format='WEBP')
        out.seek(0)

        # Random unique name
        now = datetime.now()
        name = os.path.join('images',
                            str(now.year), str(now.month), str(now.day),
                            str(uuid.uuid4()) + '.webp')

        self.image.save(name, File(ContentFile(out.read())), save=False)

        super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    writer = models.CharField(max_length=50, default="ناشناس")
    email = models.EmailField()
    date = models.DateTimeField(default=datetime.now)
    text = models.TextField(max_length=2000)
    is_accepted = models.BooleanField(default=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    replies = models.ForeignKey('Comment', on_delete=models.SET_NULL, null=True, related_name="repliedOn")

    def __str__(self):
        return f"{self.id}, " \
               f"{self.writer}, " \
               f"{self.date.strftime('%Y-%m-%d %H:%M:%S')}, " \
               f"{('' if self.is_accepted else 'Not') + ' Accepted'}, " \
               f"{textwrap.shorten(self.text, width=50, placeholder='...')}"


class Ad(models.Model):
    provider = models.CharField(max_length=50)
    url = models.URLField()

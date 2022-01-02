import textwrap
from datetime import datetime

from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="posts")
    importance = models.SmallIntegerField(default=0)
    publishDate = models.DateTimeField(default=datetime.now)
    image = models.ImageField(upload_to="images/articleMain")
    article = RichTextField()
    visits = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.id}, " \
               f"{textwrap.shorten(self.title, width=50, placeholder='...')}, " \
               f"{self.publishDate.replace(microsecond=0).isoformat(' ')}, " \
               f"{self.author.last_name}, {self.author.first_name}"


class Comment(models.Model):
    writer = models.CharField(max_length=50, default="ناشناس")
    email = models.EmailField()
    date = models.DateTimeField(default=datetime.now)
    text = models.TextField(max_length=2000)
    is_accepted = models.BooleanField(default=False)
    reply = models.OneToOneField(to='Comment', on_delete=models.SET_NULL, null=True, related_name="repliedOn")

    def __str__(self):
        return f"{self.id}, " \
               f"{self.writer}, " \
               f"{self.date.replace(microsecond=0).isoformat(' ')}, " \
               f"{('' if self.is_accepted else 'Not') + ' Accepted'}, " \
               f"{textwrap.shorten(self.text, width=50, placeholder='...')}"

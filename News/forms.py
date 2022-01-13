from django import forms

from News.models import Post


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = [
            'publish_date',
            'author',
            'visits',
        ]
        labels = {
            'title': 'عنوان',
            'importance': 'اهمیت',
            'categories': 'دسته بندی‌ها',
            'image': 'تصویر',
            'article': 'متن خبر',
        }
        help_texts = {'categories': 'برای انتخاب چند گزینه از دکمه‌ی Ctrl یا Shift استفاده کنید.'}

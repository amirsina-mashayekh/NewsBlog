from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm
from django.contrib.auth.models import User

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


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {'class': 'form-page-fields'}
    username = UsernameField(label='نام کاربری')
    password = forms.CharField(label='کلمه عبور', widget=forms.PasswordInput)


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {'class': 'form-page-fields'}
        self.fields['first_name'].widget.attrs['style'] = 'direction: rtl !important;'
        self.fields['last_name'].widget.attrs['style'] = 'direction: rtl !important;'
    first_name = forms.CharField(max_length=50, label='نام')
    last_name = forms.CharField(max_length=50, label='نام خانوادگی')
    email = forms.EmailField(label='ایمیل')
    username = UsernameField(max_length=50, label='نام کاربری')
    password1 = forms.CharField(label='کلمه عبور', widget=forms.PasswordInput)
    password2 = forms.CharField(label='تکرار کلمه عبور', widget=forms.PasswordInput)
    field_order = [
        'first_name',
        'last_name',
        'email',
        'username',
        'password1',
        'password2'
    ]

    def save(self, commit=True):
        user = User.objects.create_user(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
        )
        return user

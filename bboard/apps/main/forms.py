from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import AdvUser
from .models import user_registrated
from .models import SuperRubric, SubRubric
from .models import Bb, AdditionalImage
from .models import Comment
from .models import Answers
from .models import FeedBack

from captcha.fields import CaptchaField


class ChangeInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес ел. почты')

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'user_image', 'send_messages')


class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес ел. почты')

    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль(повторно)', widget=forms.PasswordInput,
        help_text='Введите тот же пароль')

    def clean_password1(self):
        password1 = self.cleaned_data['password1']

        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        # password1 = password1.encode('utf-8').strip()
        password2 = self.cleaned_data['password2']
        # password2 = password1.encode('utf-8').strip()

        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введенные пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False

        if commit:
            user.save()
        user_registrated.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'send_messages')


class LoginUserForm(forms.Form):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    remember_me = forms.BooleanField(label='Запомнить меня', required=False)


class PasswordResetConfirmUserForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль(повторно)', widget=forms.PasswordInput,
                                help_text='Введите тот же пароль')

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введенные пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user

    class Meta:
        model = AdvUser
        fields = ('password1', 'password2')


class PasswordResetUserForm(forms.ModelForm):
    class Meta:
        model = AdvUser
        fields = ('email',)


class SubRubricForm(forms.ModelForm):
    super_rubric = forms.ModelChoiceField(queryset=SuperRubric.objects.all(), empty_label=None,
                                          label='Надрубрика', required=True)

    class Meta:
        model = SubRubric
        fields = '__all__'


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label='Ключевое слово')
    price_from = forms.IntegerField(required=False, min_value=0, max_value=1000000, label='Цена от')
    price_to = forms.IntegerField(required=False, min_value=0, max_value=1000000, label='Цена до')


class BbForm(forms.ModelForm):
    class Meta:
        model = Bb
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}


AIFormSet = inlineformset_factory(Bb, AdditionalImage, fields='__all__')


class UserCommentForm(forms.ModelForm):
    # author = forms.CharField(disabled=True,
    #                          )
    captcha = CaptchaField(label='Введите текст с картинки',
                           error_messages={'invalid': 'Неправильный текст'})

    class Meta:
        model = Comment
        exclude = ('is_active', 'answers',)
        widgets = {'bb': forms.HiddenInput, 'author': forms.HiddenInput, }


class GuestCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('is_active', 'author', 'content', 'answers',)
        widgets = {'bb': forms.HiddenInput}


class CommentChangeForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('is_active', )
        widgets = {'bb': forms.HiddenInput, 'author': forms.HiddenInput, }


class CommentAddAnswer(forms.ModelForm):
    class Meta:
        model = Answers
        exclude = ('is_active', )
        widgets = {'bb': forms.HiddenInput, 'author': forms.HiddenInput, 'comment': forms.HiddenInput, }


class AnswerChangeForm(forms.ModelForm):
    class Meta:
        model = Answers
        exclude = ('is_active', )
        widgets = {'author': forms.HiddenInput, 'comment': forms.HiddenInput, }


class AddFeedBackForm(forms.ModelForm):
    class Meta:
        model = FeedBack
        fields = ('author', 'text', )

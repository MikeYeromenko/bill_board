from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from main.models import AdvUser, user_registrated, SubRubric, SuperRubric, Bb, AdditionalImage, Comment


class ChangeUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')

    class Meta:
        model = AdvUser
        fields = ['username', 'first_name', 'last_name', 'birth_date', 'send_messages', 'email']


class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(required=True, widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(required=True, widget=forms.PasswordInput,
                                help_text='Введите тот же самый пароль ещё раз для проверки')
    birth_date = forms.DateField(widget=forms.widgets.SelectDateWidget(empty_label=('Выберите год', 'Выберите месяц',
                                                                                    'Выберите число')))

    class Meta:
        model = AdvUser
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name',
                  'send_messages', 'birth_date']

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        forms.ModelForm.clean(self)
        password1, password2 = self.cleaned_data['password1'], self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введенные пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = forms.ModelForm.save(self, commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registrated.send(RegisterUserForm, instance=user)
        return user


class UserPasswordChangeForm(PasswordChangeForm):

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        If password was set with Python Social Auth, old password just resets
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.has_usable_password():
            return old_password
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password


class SubRubricForm(forms.ModelForm):
    super_rubric = forms.ModelChoiceField(queryset=SuperRubric.objects.all(), required=True,
                                          empty_label=None, label='надрубрика')

    class Meta:
        model = SubRubric
        exclude = ['id', ]


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label='')


class BbForm(forms.ModelForm):
    price = forms.FloatField(initial=0, min_value=0, max_value=99999999999, label='Цена')

    class Meta:
        model = Bb
        exclude = ['id',]
        widgets = {'author': forms.HiddenInput}


AIFormSet = inlineformset_factory(Bb, AdditionalImage, fields='__all__')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        exclude = ['is_active', 'parent_comment', 'likes', 'dislikes', 'complain']
        widgets = {'bb': forms.HiddenInput, 'author': forms.HiddenInput}


class UserCommentForm(CommentForm):
    author_name = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), label='Автор')


class GuestCommentForm(CommentForm):
    captcha = CaptchaField(label='Вычислите значение выражения', error_messages={'invalid': 'Неправильный текс'})



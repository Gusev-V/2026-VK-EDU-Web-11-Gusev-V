from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Login',
        widget=forms.TextInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter your login here',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter your password here',
            'autocomplete': 'current-password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = 'Sorry, wrong password!'

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label='Login',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter your login here',
            'autocomplete': 'username'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter your email here',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter your password here',
            'autocomplete': 'new-password'
        })
    )
    password_confirm = forms.CharField(
        label='Repeat Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form_input',
            'placeholder': 'Repeat your password here',
            'autocomplete': 'new-password'
        })
    )
    nickname = forms.CharField(
        label='Nickname',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter your NickName'
        })
    )
    avatar = forms.ImageField(
        label='Upload avatar',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form_input',
            'accept': 'image/png, image/jpeg, image/svg'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form_input',
                'placeholder': 'Enter your login here',
                'autocomplete': 'username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form_input',
                'placeholder': 'Enter your email here',
                'autocomplete': 'email'
            }),
        }

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError('Passwords do not match!')

        return password_confirm

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Sorry, this email address already registered!')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                nickname=self.cleaned_data['nickname'],
                avatar=self.cleaned_data.get('avatar')
            )

        return user


class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        label='Login',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter your login here',
            'autocomplete': 'username'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter your email here',
            'autocomplete': 'email'
        })
    )
    nickname = forms.CharField(
        label='Nickname',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter your NickName'
        })
    )
    avatar = forms.ImageField(
        label='Upload avatar',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form_input',
            'accept': 'image/png, image/jpeg, image/svg'
        })
    )

    class Meta:
        model = Profile
        fields = ['nickname', 'avatar']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError('Sorry, this email address already registered!')
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            self.user.email = self.cleaned_data['email']
            self.user.save()
            profile.save()
        return profile

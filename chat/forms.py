from django import forms
from django.contrib.auth.models import User

from .models import DirectMessage, Room


class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['content']


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'title']


class UserProfileForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and new_password != confirm_password:
            raise forms.ValidationError("The two password fields must match.")

        return cleaned_data

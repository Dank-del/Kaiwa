from django import forms
from .models import DirectMessage, Room

class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['content']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'title']

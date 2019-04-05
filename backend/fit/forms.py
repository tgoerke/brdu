from django import forms
from django.forms import ModelForm
from fit.models import Data

class InputForm(ModelForm):
    class Meta:
        model = Data
        fields = '__all__'


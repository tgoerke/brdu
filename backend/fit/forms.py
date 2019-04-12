from django import forms
from django.forms import ModelForm
from fit.models import Data


class InputForm(ModelForm):
    class Meta:
        model = Data
        fields = '__all__'
        widgets = {
       'number_of_labeled_cells': forms.NumberInput(attrs={'style': 'width:24ch'}),
}
    def __init__(self, *arg, **kwarg):
        super(InputForm, self).__init__(*arg, **kwarg)
        self.empty_permitted = True

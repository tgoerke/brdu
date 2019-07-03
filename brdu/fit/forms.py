from django import forms

from .models import Data, CsvFile


class InputForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = '__all__'
        widgets = {
       'number_of_labeled_cells': forms.NumberInput(attrs={'style': 'width:24ch'}),
}
    def __init__(self, *arg, **kwarg):
        super(InputForm, self).__init__(*arg, **kwarg)
        self.empty_permitted = True

class UploadForm(forms.ModelForm):
    class Meta:
        model = CsvFile
        fields = ['file', 'user_filename']
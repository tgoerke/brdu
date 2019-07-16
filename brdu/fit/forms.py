from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.urls import reverse

from .models import Data, Upload


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
        model = Upload
        fields = ['file']
        #help_texts = {
        #    "file": "Help text."
        #}
    
    def __init__(self, *arg, **kwargs):
        row = kwargs.pop('row') # get row parameter for form_action = reverse()
        super(UploadForm, self).__init__(*arg, **kwargs)
        
        self.fields['file'].help_text = 'Upload your data in CSV format with <br /> column order as in the table on the left.'

        self.helper = FormHelper()
        self.helper.form_id = 'id-uploadForm'
        #self.helper.form_class = ''
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('fit:upload', kwargs={'row': row}) # , css_class='btn btn-primary'
        self.helper.add_input(Submit('submit', 'Upload'))
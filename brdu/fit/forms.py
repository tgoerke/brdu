from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder # , Field
from crispy_forms.bootstrap import FormActions
from django.urls import reverse

from .utils import MyErrorList

from .models import Data, Upload

class InputForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = [
            'measurement_time',
            'number_of_labeled_cells',
            'number_of_all_cells',
        ] #'__all__'
        #widgets = {field: forms.NumberInput(attrs={'style': 'width:24ch'}) for field in fields}

    def __init__(self, *args, **kwargs):
        super(InputForm, self).__init__(*args, **kwargs)
        self.error_class = MyErrorList # https://stackoverflow.com/questions/2125717/django-forms-error-class

        self.empty_permitted = True
        
        """
        # Crispy Forms
        self.helper = FormHelper()
        self.helper.form_id = 'id-experimentalDataFormset'
        #self.helper.form_class = ''
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('fit:form', kwargs={'row': row})
        self.helper.add_input(Submit('calc', 'Calculate', css_class='btn btn-primary'))
        self.helper.add_input(Submit('clear', 'Clear all data'))
        self.helper.add_input(Submit('add', 'Add 10 rows'))
        self.helper.add_input(Submit('update', 'Clear empty lines'))
        """

class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['file']
        help_text = 'Upload your data in CSV format with <br /> column order as in the table on the left.'
        #help_texts = {
        #    "file": "Help text."
        #}
    
    def __init__(self, *args, **kwargs):
        #row = kwargs.pop('row') # get row parameter for form_action = reverse()
        super(UploadForm, self).__init__(*args, **kwargs)

        self.error_class = MyErrorList
        
        """
        self.helper = FormHelper()
        
        # self.helper.layout = Layout(
        #     Fieldset('Or upload CSV file:',
        #         Field('file',
        #         ),
        #     ),
        # )

        self.helper.form_id = 'id-uploadForm'
        #self.helper.form_class = ''
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('fit:upload', kwargs={'row': row})
        self.helper.add_input(Submit('submit', 'Upload', css_class="btn-secondary"))
        self.fields['file'].help_text = 'Upload your data in CSV format with <br /> column order as in the table on the left.'
        """
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views import generic

from .models import Data
from .calc import calc

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from .forms import InputForm
from django.forms import formset_factory
from django.shortcuts import redirect
import json

# Rendering
from .utils import MyErrorList
from django.forms.utils import ErrorList

# CSV upload
from .forms import UploadForm
from .models import Upload
from .validators import ValidateFileType
import pandas as pd
from django.conf import settings

# Plot
from .models import Assay
from django.core.files.base import ContentFile
import os
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import get_object_or_404

# Debugging and logging
from IPython import embed
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def form(request):
    #embed()

    row_query_string = request.GET.get('rows', '10') # Get query string (?row=...)
    try:
        row = int(row_query_string)
    except:
        row = 10

    InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=row, validate_min=False)
    upload_form = UploadForm(row=row)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        #form = InputForm(request.POST)
        formset = InputFormSet(request.POST, request.FILES, form_kwargs={'row': row}) # https://docs.djangoproject.com/en/2.2/topics/forms/formsets/#passing-custom-parameters-to-formset-forms

        #formset = InputFormSet(request.FILES)
        if 'clear' in request.POST:
            request.session["data"] = []
            return redirect('fit:index')
        if 'add' in request.POST:
            run_add = True
        else:
            run_add = False
        if 'calc' in request.POST:
            run_calc = True
        else:
            run_calc = False
        if 'update' in request.POST:
            run_update = True
        else:
            run_update = False

        # check whether it's valid:
        if formset.is_valid():
            data_form = formset.cleaned_data
            times=[];datas=[];ncells=[];
            for i in data_form:
                print( len(i),i)
                if len(i) == 3:
                        print("asdasdasdsa")
                        times.append(i['measurement_time'])
                        datas.append(i['number_of_labeled_cells'])
                        ncells.append(i['number_of_all_cells'])
            #save data
            data = [i for i in zip(times,datas,ncells)]
            print(data)
            request.session["data"] = data
            #hack to detelte data
            init_data = [{'measurement_time': i, 'number_of_labeled_cells': k, 'number_of_all_cells': l} for i,k,l in request.session['data']]
            formset = InputFormSet(initial=init_data, form_kwargs={'row': row})
            if run_calc:
                if len(ncells) == len(datas) and len(datas) == len(times) and len(times)>0:
                    results, plot = calc(ncells,times,datas)

                    # Save plot in media folder; save corresponding database entry.
                    # https://docs.djangoproject.com/en/2.2/ref/files/file/#additional-methods-on-files-attached-to-objects
                    assay = Assay()

                    # Get the 'Session' instance
                    if not request.session.session_key: # New client: no session saved for assignment to assay-Model yet.
                        request.session.save()
                    session = get_object_or_404(Session, session_key=request.session.session_key) # Generate 'Session' instance from 'SessionStore' object.
                    # session = Session.objects.get(session_key=request.session.session_key)

                    # Link temporarily stored assay data to current session
                    assay.session = session
                    assay.plot.save('dummy.png', ContentFile(plot), save=False) # filename will be randomized anyway
                    assay.save()
                    #plot_filename = os.path.basename(assay.plot.name) # only filename, not the whole path
                    return render(request, 'cell2.html', {'formset': formset, 'fit': results, 'assay': assay, 'row': row, 'upload_form': upload_form})
            if run_add:
                url = '{:s}?rows={:d}'.format(reverse('fit:form'), row+10)
                return redirect(url)
            if run_update:
                url = '{:s}?rows={:d}'.format(reverse('fit:form'), len(ncells))
                return redirect(url)

            return render(request, 'cell2.html', {'formset': formset, 'row': row, 'upload_form': upload_form})

        else:
            print(formset)
            print(formset.errors)
    # if a GET (or any other method) we'll create a blank form
    else:
        if "data" in request.session:
            init_data = [{'measurement_time': i, 'number_of_labeled_cells': k, 'number_of_all_cells': l} for i,k,l in request.session['data']]
            formset = InputFormSet(initial=init_data, form_kwargs={'row': row}) 
        else:
            formset = InputFormSet(form_kwargs={'row': row})
    #embed()
    context = {'formset': formset,'row': row, 'upload_form': upload_form}
    return  render(request, 'cell2.html', context)

def upload(request):

    row_query_string = request.GET.get('rows', '10') # Get query string (?row=...)
    try:
        row = int(row_query_string)
    except:
        row = 10

    if request.method != 'POST':
        # No data submitted; create a blank upload_form.
        upload_form = UploadForm(row=row)

        # No data submitted; create blank formset or formset with old data.
        InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=row, validate_min=False)
        if "data" in request.session:
            init_data = [{'measurement_time': i, 'number_of_labeled_cells': k, 'number_of_all_cells': l} for i,k,l in request.session['data']]
            formset = InputFormSet(initial=init_data, form_kwargs={'row': row}) 
        else:
            formset = InputFormSet(form_kwargs={'row': row})
    else:
        # POST data submitted; process data.
        upload_form = UploadForm(request.POST, request.FILES, row=row)
        if upload_form.is_valid():
            upload = upload_form.save()

            # Parse CSV file and overwrite formset data
            df = pd.read_csv(upload.file, header=None, names=['measurement_time', 'number_of_labeled_cells', 'number_of_all_cells'])
            init_data = df.to_dict('records')
            InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=row, validate_min=False)
            formset = InputFormSet(initial=init_data, form_kwargs={'row': row})
            row = len(init_data)
            InputFormSet.min_num = row # Clear empty lines

            # Delete file
            #upload.file.delete() # delete CSV file; Is done now by 'django_cleanup' automatically.
            upload.delete() # delete database entry
        else:
            # Invalid form, use old data.
            InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=row, validate_min=False)
            if "data" in request.session:
                init_data = [{'measurement_time': i, 'number_of_labeled_cells': k, 'number_of_all_cells': l} for i,k,l in request.session['data']]
                formset = InputFormSet(initial=init_data, form_kwargs={'row': row}) 
            else:
                formset = InputFormSet(form_kwargs={'row': row})

    context = {'row': row, 'formset': formset, 'upload_form': upload_form}
    return render(request, 'cell2.html', context)
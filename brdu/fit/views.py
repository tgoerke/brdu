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

# Debugging and logging
from IPython import embed
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def form(request,row=10):
    InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=row, validate_min=False)
    upload_form = UploadForm(row=row)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        #form = InputForm(request.POST)
        formset = InputFormSet(request.POST, request.FILES)
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
            formset = InputFormSet(initial=init_data)
            if run_calc:
                if len(ncells) == len(datas) and len(datas) == len(times) and len(times)>0:
                    results, plot = calc(ncells,times,datas)

                    # Save plot to media/database
                    # https://docs.djangoproject.com/en/2.2/ref/files/file/#additional-methods-on-files-attached-to-objects
                    assay = Assay()

                    # Link temporary stored assay data to current session
                    session = Session.objects.get(session_key=request.session.session_key)
                    assay.session = session
                    
                    assay.plot.save('dummy.png', ContentFile(plot), save=False) # filename will be randomized anyway
                    assay.save()
                    #plot_filename = os.path.basename(assay.plot.name) # only filename, not the whole path
                    
                    return render(request, 'cell2.html', {'formset': formset, 'fit': results, 'assay': assay, 'row': row, 'upload_form': upload_form})
            if run_add:
                return redirect('fit:form', row=row+10)
            if run_update:
                return redirect('fit:form', row=len(ncells))

            return render(request, 'cell2.html', {'formset': formset, 'row': row, 'upload_form': upload_form})

        else:
            print(formset)
            print(formset.errors)
    # if a GET (or any other method) we'll create a blank form
    else:
        if "data" in request.session:
            init_data = [{'measurement_time': i, 'number_of_labeled_cells': k, 'number_of_all_cells': l} for i,k,l in request.session['data']]
            formset = InputFormSet(initial=init_data) 
        else:
            formset = InputFormSet()

    return  render(request, 'cell2.html', {'formset': formset,'row': row, 'upload_form': upload_form})

def upload(request, row=10):
    if request.method != 'POST':
        # No data submitted; create a blank upload_form.
        upload_form = UploadForm(row=row)

        # No data submitted; create blank formset or formset with old data.
        InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=row, validate_min=False)
        if "data" in request.session:
            init_data = [{'measurement_time': i, 'number_of_labeled_cells': k, 'number_of_all_cells': l} for i,k,l in request.session['data']]
            formset = InputFormSet(initial=init_data) 
        else:
            formset = InputFormSet()
    else:
        # POST data submitted; process data.
        upload_form = UploadForm(request.POST, request.FILES, row=row)
        if upload_form.is_valid():
            upload = upload_form.save()

            # Parse CSV file and overwrite formset data
            df = pd.read_csv(upload.file, header=None, names=['measurement_time', 'number_of_labeled_cells', 'number_of_all_cells'])
            init_data = df.to_dict('records')
            InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=row, validate_min=False)
            formset = InputFormSet(initial=init_data)
            row = len(init_data)
            InputFormSet.min_num = row # Clear empty lines

            # Delete file
            upload.file.delete() # delete CSV file
            upload.delete() # delete database entry
        else:
            # Invalid form, use old data.
            InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=row, validate_min=False)
            if "data" in request.session:
                init_data = [{'measurement_time': i, 'number_of_labeled_cells': k, 'number_of_all_cells': l} for i,k,l in request.session['data']]
                formset = InputFormSet(initial=init_data) 
            else:
                formset = InputFormSet()

    context = {'row': row, 'formset': formset, 'upload_form': upload_form}
    return render(request, 'cell2.html', context)
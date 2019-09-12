from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views import generic

from .models import Data

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

# Download
from django.http import HttpResponse, Http404

# Calculation
from .calc import calc
import timeit

# Plot
from django.core.files.base import ContentFile
import os
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import get_object_or_404

# Data storage (plots, CSV files)
from .models import Assay
from datetime import datetime
from .utils import unique_file_path

# Data for sharing
from .models import SharedExperiment
from .utils import generate_share_id
from django.db.utils import IntegrityError

# Debugging and logging
from IPython import embed
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def form(request):
    row_query_string = request.GET.get('rows', '10') # Get query string (?row=...)
    try:
        row = int(row_query_string)
    except:
        row = 10

    InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=row, validate_min=False)
    upload_form = UploadForm()
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        #form = InputForm(request.POST)
        formset = InputFormSet(request.POST, request.FILES) # https://docs.djangoproject.com/en/2.2/topics/forms/formsets/#passing-custom-parameters-to-formset-forms

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
            times = []
            datas = []
            ncells = []
            for i in data_form:
                print(len(i), i)
                if len(i) == 3:
                        print("asdasdasdsa")
                        times.append(i['measurement_time'])
                        datas.append(i['number_of_labeled_cells'])
                        ncells.append(i['number_of_all_cells'])
            # save data
            data = [i for i in zip(times,datas,ncells)]
            print(data)
            request.session["data"] = data
            # hack to delete data
            init_data = [{'measurement_time': i, 'number_of_labeled_cells': k, 'number_of_all_cells': l} for i,k,l in request.session['data']]
            formset = InputFormSet(initial=init_data)
            if run_calc:
                if len(ncells) == len(datas) and len(datas) == len(times) and len(times) > 0:
                    # Calculation
                    start_time = timeit.default_timer() # Measure the time for calculation; https://docs.python.org/3.7/library/timeit.html
                    results, plot = calc(ncells,times,datas) # Run calculation.
                    run_time = round(timeit.default_timer() - start_time, 3)
                    logger.debug('Calculation finished after {} s.'.format(run_time))

                    # Get the 'Session' instance
                    if not request.session.session_key: # New client: no session saved for assignment to assay-Model yet.
                        request.session.save()
                    session = get_object_or_404(Session, session_key=request.session.session_key) # Generate 'Session' instance from 'SessionStore' object.
                    # session = Session.objects.get(session_key=request.session.session_key) # get object, but exception will raised if not existing

                    # Try to load old assay instance
                    try:
                        assay = Assay.objects.get(session_id=session.session_key)
                    except Assay.DoesNotExist: # no assay data for this session yet
                        assay = Assay()
                        assay.session = session

                    # Save input and results
                    assay.experimental_data = data
                    assay.run_time = run_time
                    assay.calculation_results = results

                    # Save plot in media folder; save corresponding database entry; https://docs.djangoproject.com/en/2.2/ref/files/file/#additional-methods-on-files-attached-to-objects
                    #plot_filename = os.path.basename(assay.plot.name) # only filename, not the whole path
                    assay.plot.save('dummy.png', ContentFile(plot), save=False) # Filename doesn't matter, will be randomized anyway in course of this call.
                    assay.save()
                    
                    # Prepare sharing
                    shared_experiment = SharedExperiment()
                    
                    share_id_collisions = 0
                    unique_id_found = False
                    while unique_id_found == False:
                        unique_id_found = True
                        share_id = generate_share_id() # Generate share id for this calculation
                        shared_experiment.share_id = share_id
                        shared_experiment.id_collision_count = share_id_collisions

                        try:
                            shared_experiment.save()
                        except IntegrityError as error: # duplicate share id generated
                            if any('UNIQUE constraint failed' in str(s) for s in error.args):
                                share_id_collisions += 1
                                unique_id_found = False
                                logger.warning('Share ID collision detected. ID: {:s}; Counter: {:d}'.format(share_id, share_id_collisions))
                            else: # raise all other IntegrityErrors
                                raise error
                    
                    context = {'formset': formset, 'fit': results, 'assay': assay, 'row': row, 'upload_form': upload_form}
                    return render(request, 'cell2.html', context)

            if run_add:
                url = '{:s}?rows={:d}'.format(reverse('fit:form'), row+10)
                return redirect(url)
            if run_update:
                url = '{:s}?rows={:d}'.format(reverse('fit:form'), len(ncells))
                return redirect(url)

            context = {'formset': formset, 'row': row, 'upload_form': upload_form}
            return render(request, 'cell2.html', context)

        else:
            print(formset)
            print(formset.errors)
    # If it's a GET request (or any other), we'll create a blank form.
    else:
        if "data" in request.session:
            init_data = [{'measurement_time': i, 'number_of_labeled_cells': k, 'number_of_all_cells': l} for i,k,l in request.session['data']]
            formset = InputFormSet(initial=init_data) 
        else:
            formset = InputFormSet()

    context = {'formset': formset,'row': row, 'upload_form': upload_form}
    return  render(request, 'cell2.html', context)

def share(request):
    row_query_string = request.GET.get('rows', '10') # Get query string (?row=...)
    try:
        row = int(row_query_string)
    except:
        row = 10

def upload(request):
    row_query_string = request.GET.get('rows', '10') # Get query string (?row=...)
    try:
        row = int(row_query_string)
    except:
        row = 10

    if request.method != 'POST':
        # No data submitted; create a blank upload_form.
        upload_form = UploadForm()

        # No data submitted; create blank formset or formset with old data.
        InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=row, validate_min=False)
        if "data" in request.session: # old data
            init_data = [{'measurement_time': i, 'number_of_labeled_cells': k, 'number_of_all_cells': l} for i,k,l in request.session['data']]
            formset = InputFormSet(initial=init_data) 
        else: # blank form
            formset = InputFormSet()
    else:
        # POST data submitted; process data.
        upload_form = UploadForm(request.POST, request.FILES)
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
            #upload.file.delete() # delete CSV file; Is done now by 'django_cleanup' automatically.
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

def download(request):
    filename = request.GET.get('file', '') # ?file=...
    destination = request.GET.get('destination', 'user') # &destination=...

    # Validate file path.
    subdir = 'downloads' # Folder, where the downloadable files are located.
    download_path = os.path.join(settings.STATIC_ROOT, subdir)
    file_path = os.path.abspath(os.path.join(download_path, filename))

    if download_path not in file_path: # User is trying to access file outside allowed download_path.
        raise Http404
    else:
        if destination == 'user': # Let the browser download the file.
            if os.path.isfile(file_path): # User requests a file and not a folder; https://stackoverflow.com/a/36394206/7192373
                with open(file_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type="text/plain")
                    response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path) # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition#Syntax
                    return response
            else:
                raise Http404
        elif destination == 'form': # Fill formset with example data.
            if os.path.isfile(file_path):
                # Parse CSV file
                with open(file_path, 'rb') as f:
                    df = pd.read_csv(f, header=None, names=['measurement_time', 'number_of_labeled_cells', 'number_of_all_cells'])
                init_data = df.to_dict('records')

                # Create empty forms
                InputFormSet = formset_factory(InputForm,extra=0,can_delete=False)
                upload_form = UploadForm()

                # Overwrite formset data
                formset = InputFormSet(initial=init_data)
                row = len(init_data)
                InputFormSet.min_num = row # Clear empty lines

                context = {'row': row, 'formset': formset, 'upload_form': upload_form, 'csv_inserted': True}
                return render(request, 'cell2.html', context)
            else: # Non-existing file.
                raise Http404
        else: # Undefined destination.
            raise Http404

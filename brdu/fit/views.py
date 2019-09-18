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
from django.core.exceptions import FieldError

# Debugging and logging
from IPython import embed
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def form(request):
    rows = request.session.get('rows', 10)

    # Make sure, used row number is not less than the length of data rows
    if 'data' in request.session:
        if rows < len(request.session['data']):
            rows = len(request.session['data'])

    InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=rows, validate_min=False)
    upload_form = UploadForm()
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        #form = InputForm(request.POST)
        formset = InputFormSet(request.POST, request.FILES) # https://docs.djangoproject.com/en/2.2/topics/forms/formsets/#passing-custom-parameters-to-formset-forms

        #formset = InputFormSet(request.FILES)
        if 'clear' in request.POST:
            request.session['data'] = []
            request.session['rows'] = 10
            return redirect('fit:form')

        # check whether it's valid:
        if formset.is_valid():
            data_form = formset.cleaned_data
            times = []
            datas = []
            ncells = []
            for i in data_form:
                print(len(i), i)
                if len(i) == 3:
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

            if 'calc' in request.POST:
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
                    plot = {'filepath_relative': assay.filename}

                    # Prepare sharing
                    share = {}
                    experiment_id_collisions = 0
                    shared_experiment_id_collisions = 0
                    unique_id_found = False
                    while not unique_id_found: # Generate unique share id for this calculation.
                        share['id'] = generate_share_id()
                        assay.share_id = share['id']
                        assay.experiment_id_collisions = experiment_id_collisions
                        assay.shared_experiment_id_collisions = shared_experiment_id_collisions

                        if not SharedExperiment.objects.filter(share_id=share['id']).exists(): # Check in sharing table for collisions; https://docs.djangoproject.com/en/3.0/ref/models/querysets/#exists
                            """
                            Collisions can occur in the Assay table with temporary
                            stored results and preliminary share id or in the SharedExperiment
                            table, where the permanently stored/shared results are.
                            """
                            try:
                                assay.save()
                                unique_id_found = True
                            except IntegrityError as error: # Share id already exists in Assay table.
                                if any('UNIQUE constraint failed' in str(s) for s in error.args):
                                    shared_experiment_id_collisions += 1
                                    logger.warning('Share ID collision detected in table Assay. ID: {:s}; Counter: {:d}'.format(share['id'], shared_experiment_id_collisions))
                                else: # raise all other IntegrityErrors
                                    raise error
                        else: # Share id already exists in SharedExperiment table.
                            experiment_id_collisions += 1
                            logger.warning('Share ID collision detected in table SharedExperiment. ID: {:s}; Counter: {:d}'.format(share['id'], experiment_id_collisions))

                    context = {'formset': formset, 'results': results, 'plot': plot, 'row': rows, 'upload_form': upload_form, 'share': share}
                    return render(request, 'cell2.html', context)

            if 'add' in request.POST:
                rows += 10
                request.session['rows'] = rows
                return redirect('fit:form')
            if 'update' in request.POST:
                rows = len(ncells)
                request.session['rows'] = rows
                return redirect('fit:form')

            context = {'formset': formset, 'row': rows, 'upload_form': upload_form}
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

    context = {'formset': formset, 'row': rows, 'upload_form': upload_form}
    return  render(request, 'cell2.html', context)

def share(request, share_id):
    """
    Loads shared experiment.
    If a share id is queried for the first time, the experimental data
    is copied to the sharing db table (from the session-based assay table)
    for permanent storage.
    """

    share = {}
    share['shared'] = True # Flag to tell the template that it's loading a sharing site.
    share['id'] = share_id

    # Load shared experiment
    try:
        shared_experiment = SharedExperiment.objects.get(share_id=share_id) # == GET-Request
        share['new'] = False
        shared_experiment.save() # Resave DB entry in order to update "date_last_visited"
    except (SharedExperiment.DoesNotExist, FieldError): # Sharing link is called for the first time; == POST-Request
        experiment = get_object_or_404(Assay, share_id=share_id)
        share['new'] = True

        # Store experiment dataset in database permanently
        shared_experiment = SharedExperiment()
        shared_experiment.share_id = share_id
        shared_experiment.experiment_id_collisions = experiment.experiment_id_collisions
        shared_experiment.shared_experiment_id_collisions = experiment.shared_experiment_id_collisions
        shared_experiment.experimental_data = experiment.experimental_data
        shared_experiment.run_time = experiment.run_time
        shared_experiment.calculation_results = experiment.calculation_results
        shared_experiment.plot.save('shared/filename.png', content=experiment.plot.file, save=False)

        shared_experiment.save()

    # Load data, plot, results
    InputFormSet = formset_factory(InputForm, extra=0, can_delete=False, validate_min=False)
    init_data = [{'measurement_time': i, 'number_of_labeled_cells': k, 'number_of_all_cells': l} for i,k,l in shared_experiment.experimental_data]
    formset = InputFormSet(initial=init_data)

    filepath_absolute = shared_experiment.plot.name
    filepath_relative = filepath_absolute.replace(settings.MEDIA_ROOT + '/', '') 
    #plot = {'filename': os.path.basename(shared_experiment.plot.name)}
    plot = {'filepath_relative': filepath_relative}

    upload_form = UploadForm()

    context = {'formset': formset, 'upload_form': upload_form, 'share': share, 'results': shared_experiment.calculation_results, 'plot': plot}
    return render(request, 'cell2.html', context)

def upload(request):
    rows = request.session.get('rows', 10)

    if request.method != 'POST':
        # No data submitted; create a blank upload_form.
        upload_form = UploadForm()

        # No data submitted; create blank formset or formset with old data.
        InputFormSet = formset_factory(InputForm, extra=0, can_delete=False, min_num=rows, validate_min=False)
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
            InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=rows, validate_min=False)
            formset = InputFormSet(initial=init_data)
            
            rows = len(init_data)
            InputFormSet.min_num = rows # Clear empty lines
            request.session['rows'] = rows # Save new number of rows in session.

            # Delete file
            #upload.file.delete() # delete CSV file; Is done now by 'django_cleanup' automatically.
            upload.delete() # delete database entry
        else:
            # Invalid form, use old data.
            InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=rows, validate_min=False)
            if "data" in request.session:
                init_data = [{'measurement_time': i, 'number_of_labeled_cells': k, 'number_of_all_cells': l} for i,k,l in request.session['data']]
                formset = InputFormSet(initial=init_data) 
            else:
                formset = InputFormSet()

    context = {'row': rows, 'formset': formset, 'upload_form': upload_form}
    return render(request, 'cell2.html', context)

def download(request):
    # Handle query strings.
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
                rows = len(init_data)
                InputFormSet.min_num = rows # Clear empty lines
                request.session['rows'] = rows # Save new number of rows in session.

                context = {'row': rows, 'formset': formset, 'upload_form': upload_form, 'csv_inserted': True}
                return render(request, 'cell2.html', context)
            else: # Non-existing file.
                raise Http404
        else: # Undefined destination.
            raise Http404

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views import generic

from fit.models import Data
from .calc import calc

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import InputForm
from django.forms import formset_factory

import json

def form(request):
    InputFormSet = formset_factory(InputForm, extra=5)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        #form = InputForm(request.POST)
        formset = InputFormSet(request.POST, request.FILES)
        # check whether it's valid:
        data_form = formset.cleaned_data
        if formset.is_valid():
            times=[];datas=[];ncells=[];
            for i in data_form:
                try:
                    times.append(i['measurement_time'])
                    datas.append(i['labeled_cells'])
                    ncells.append(i['number_of_cells'])
                except:
                    pass
            if len(ncells) == len(datas) and len(datas) == len(times) and len(times)>0:
                results = calc(ncells,times,datas)
            else:
                results = calc()
            return render(request, 'cell2.html', { 'formset': formset, 'fit': results })
    # if a GET (or any other method) we'll create a blank form
    else:
        formset = InputFormSet()

    return render(request, 'cell2.html', {'formset': formset})


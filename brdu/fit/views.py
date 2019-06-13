from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views import generic

from fit.models import Data
from .calc import calc

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from .forms import InputForm
from django.forms import formset_factory
from django.shortcuts import redirect
import json



def form(request,row=20):
    InputFormSet = formset_factory(InputForm,extra=0,can_delete=False, min_num=row, validate_min=False)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        #form = InputForm(request.POST)
        formset = InputFormSet(request.POST, request.FILES)
        if 'clear' in request.POST:
            request.session["data"] =[]
            return HttpResponseRedirect(reverse('fit:form', args=[10]))
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
                    results = calc(ncells,times,datas)
                    return render(request, 'cell2.html', { 'formset': formset, 'fit': results,'row':row })
            if run_add:
                return HttpResponseRedirect(reverse('fit:form', args=[row+10]))
            if run_update:
                return HttpResponseRedirect(reverse('fit:form', args=[len(ncells)]))
            return render(request, 'cell2.html', { 'formset': formset, 'row':row })

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

    return  render(request, 'cell2.html', {'formset': formset,'row':row})


from django.contrib import admin
from django.urls import path, include

from django.urls import path, re_path

from . import views
from django.views.generic import RedirectView
#from .views import ListExperimentsView
#from .views import FileView

urlpatterns = [
    #path('admin/', admin.site.urls),
    #path('', views.index, name='index'),
    #path('',  RedirectView.as_view(url='/row=10'), name='cellcycle'),
    path('', views.form, name='cellcycle'),
    path('index.html', views.form, name='cellcycle'),
    path('row=<int:row>', views.form, name='cellcycle'),
    #path('experiments/', ListExperimentsView.as_view(), name="experiments-all"),
    #path('upload/', FileView.as_view(), name='file-upload'),
]

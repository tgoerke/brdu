from django.contrib import admin
from django.urls import path, include

from django.urls import path, re_path

from . import views
from django.views.generic import RedirectView
#from .views import ListExperimentsView
#from .views import FileView

app_name = 'fit'
urlpatterns = [
    #path('', views.index, name='index'),
    #path('',  RedirectView.as_view(url='/row=10'), name='cellcycle'),
    path('', views.form, name='index'),
    path('index.html', views.form, name='index_html'),
    path('', views.form, name='form'),
    path('', views.form, name='result'),
    path('share/<str:share_id>/', views.share, name='share'),
    #path('share/', views.share, name='share'),
    path('upload/', views.upload, name='upload'),
    path('download/', views.download, name='download')
    #path('experiments/', ListExperimentsView.as_view(), name="experiments-all"),
    #path('upload/', FileView.as_view(), name='file-upload'),
]

from django.contrib import admin
from django.urls import path, include

from django.urls import path

from . import views
from .views import ListExperimentsView
from .views import FileView

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('experiments/', ListExperimentsView.as_view(), name="experiments-all"),
    path('upload/', FileView.as_view(), name='file-upload'),
]

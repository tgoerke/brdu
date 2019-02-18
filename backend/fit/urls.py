from django.contrib import admin
from django.urls import path, include

from django.urls import path

from . import views
from .views import ListExperimentsView

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('experiments/', ListExperimentsView.as_view(), name="experiments-all")
]

from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Experiments

admin.site.register(Experiments)

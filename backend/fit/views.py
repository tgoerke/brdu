from django.http import HttpResponse

from rest_framework import generics
from .models import Experiments
from .serializers import ExperimentSerializer


def index(request):
    return HttpResponse("Hello, world. You're at the fit index.")

class ListExperimentsView(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    queryset = Experiments.objects.all()
    serializer_class = ExperimentSerializer


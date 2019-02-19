from django.http import HttpResponse
from .calc import calc

from rest_framework import generics
from .models import Experiments
from .serializers import ExperimentSerializer


def index(request):
    #queryset = Experiments.objects.all()
    #results = calc()
    #return Response({'experiments': result})

    return HttpResponse("Hello, world. You're at the fit index.")

class ListExperimentsView(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    results = calc()
    queryset = Experiments.objects.all()
    serializer_class = ExperimentSerializer


from django.http import HttpResponse
from .calc import calc

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Experiments
from .serializers import ExperimentSerializer
from .serializers import FileSerializer


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

class FileView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
      file_serializer = FileSerializer(data=request.data)
      if file_serializer.is_valid():
        file_serializer.save()
        return Response(file_serializer.data, status=status.HTTP_201_CREATED)
      else:
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

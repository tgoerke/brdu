from rest_framework import serializers
from .models import Experiments
from .models import File


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiments
        fields = ("title", "labeling_fraction")

class FileSerializer(serializers.ModelSerializer):
    class Meta():
      model = File
      fields = ('file', 'remark', 'timestamp')

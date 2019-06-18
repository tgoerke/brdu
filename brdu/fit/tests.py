from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from .models import Experiments
from .serializers import ExperimentSerializer

# tests for views


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_experiment(title="", labeling_fraction=""):
        if title != "" and labeling_fraction != "":
            Experiments.objects.create(title=title, labeling_fraction=labeling_fraction)

    def setUp(self):
        # add test data
        self.create_experiment("exp1", "5")


class GetAllExperimentsTest(BaseViewTest):

    def test_get_all_experiments(self):
        """
        This test ensures that all experiments added in the setUp method
        exist when we make a GET request to the experiments/ endpoint
        """
        # hit the API endpoint
        response = self.client.get(
            reverse("experiments-all", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = Experiments.objects.all()
        serialized = ExperimentSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

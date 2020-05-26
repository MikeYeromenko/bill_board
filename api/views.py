from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet

from api.serializers import BbSerializer
from main.models import Bb


class BbViewSet(ModelViewSet):
    serializer_class = BbSerializer
    queryset = Bb.objects.filter(is_active=True)

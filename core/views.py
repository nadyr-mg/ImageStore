from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from core.models import Image
from core.serializers import ImagesSerializer


class ImagesView(mixins.CreateModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    queryset = Image.objects.all()
    serializer_class = ImagesSerializer

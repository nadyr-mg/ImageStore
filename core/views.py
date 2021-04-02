from rest_framework import mixins
from rest_framework.parsers import FormParser
from rest_framework.viewsets import GenericViewSet

from core.models import Image
from core.serializers import ImageSerializer
from core.utils import MultipartAnnotationParser


class ImageView(mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                GenericViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultipartAnnotationParser, FormParser,)  # content type: multipart/form-data

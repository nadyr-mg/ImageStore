from django.http import FileResponse
from rest_framework import mixins
from rest_framework.parsers import FormParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import RetrieveAPIView

from core.models import Image, Annotation
from core.serializers import ImageSerializer, AnnotationSerializer
from core.utils import MultipartJsonParser


class ImageView(mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                GenericViewSet):
    queryset = Image.objects.all()
    lookup_field = 'file'
    serializer_class = ImageSerializer

    parser_classes = (MultipartJsonParser, FormParser,)  # content type: multipart/form-data

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        file_handle = instance.file.open()

        extension = instance.file.name.rpartition('.')[2] or '*'
        response = FileResponse(file_handle, content_type=f'image/{extension}')
        response['Content-Length'] = instance.file.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % instance.file.name

        return response


class AnnotationView(mixins.RetrieveModelMixin,
                     GenericViewSet):
    queryset = Annotation.objects.all()
    lookup_field = 'image__file'
    serializer_class = AnnotationSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

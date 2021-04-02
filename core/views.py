from django.http import FileResponse
from rest_framework import mixins, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.parsers import FormParser
from rest_framework.response import Response
from rest_framework.status import HTTP_501_NOT_IMPLEMENTED
from rest_framework.viewsets import GenericViewSet

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


class AnnotationView(RetrieveUpdateAPIView):
    queryset = Annotation.objects.all()
    lookup_field = 'image__file'
    serializer_class = AnnotationSerializer

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

from django.utils.text import get_valid_filename
from rest_framework import serializers
from django.db import transaction

from core.models import Image, Annotation, Label


class LabelSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    annotation_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = Label
        fields = ['annotation_id', 'id', 'class_id', 'surface', 'shape', 'meta']

    def validate_id(self, id_):
        if Label.objects.filter(id=id_).exists():
            raise serializers.ValidationError(f'Label with this id already exists: {id_}')
        return id_


class AnnotationSerializer(serializers.ModelSerializer):
    image_id = serializers.IntegerField(required=False, write_only=True)
    labels = LabelSerializer(required=False, many=True)

    class Meta:
        model = Annotation
        fields = ['image_id', 'labels']

    @transaction.atomic
    def create(self, validated_data):
        labels_data = validated_data.pop('labels', None)
        annotation = super().create(validated_data)

        if labels_data:
            for label in labels_data:
                label['annotation_id'] = annotation.id

            serializer = LabelSerializer(data=labels_data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return annotation


class ImageSerializer(serializers.ModelSerializer):
    SUPPORTED_FORMATS = ['JPEG', 'PNG', 'TIFF']
    FILE_MAX_SIZE = 20 * 1024 * 1024  # in MB

    annotation = AnnotationSerializer(write_only=True, required=False)

    class Meta:
        model = Image
        fields = ['file', 'annotation']

    def to_internal_value(self, data):
        data = dict(data)
        for key, val in data.items():
            if val:
                data[key] = val[0]  # unpack data from multipart format

        return super().to_internal_value(data)

    def validate_file(self, file):
        filename = get_valid_filename(file.name)
        if Image.objects.filter(file=filename).exists():
            raise serializers.ValidationError('File already exists')

        if file.image.format not in self.SUPPORTED_FORMATS:
            raise serializers.ValidationError(f'{file.image.format} format is not supported. '
                                              f'Supported formats: {self.SUPPORTED_FORMATS}')

        if file.size > self.FILE_MAX_SIZE:
            raise serializers.ValidationError(f'Your file is too big. Maximum size is {self.FILE_MAX_SIZE} MB')

        return file

    def to_representation(self, instance):
        return {'id': instance.file.name}

    @transaction.atomic
    def create(self, validated_data):
        annotation_data = validated_data.pop('annotation', None)
        image = super().create(validated_data)

        if annotation_data:
            annotation_data['image_id'] = image.id
            serializer = AnnotationSerializer(data=annotation_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return image

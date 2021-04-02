from collections import OrderedDict

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
        export_fields = ['id', 'class_id', 'surface']  # fields used when query param format=export


class AnnotationSerializer(serializers.ModelSerializer):
    EXPORT_FORMAT_KEY = 'export'

    image_id = serializers.IntegerField(required=False, write_only=True)
    labels = LabelSerializer(required=False, many=True)

    class Meta:
        model = Annotation
        fields = ['image_id', 'labels']

    def to_representation(self, instance):
        result = super().to_representation(instance)

        format_param = self.context['request'].query_params.get('format', '')
        if format_param.lower() == self.EXPORT_FORMAT_KEY:
            result['labels'] = list(filter(lambda o: o['meta'].get('confirmed'),  result['labels']))

            for idx, label in enumerate(result['labels']):
                label = OrderedDict((key, val) for key, val in label.items()
                                    if key in LabelSerializer.Meta.export_fields)
                label['surface'] = ''.join(label['surface'])
                result['labels'][idx] = label

        return result

    @staticmethod
    def check_existing_labels(validated_data):
        ids = [label['id'] for label in validated_data if 'id' in label]
        existing_labels = Label.objects.filter(id__in=ids).values_list('id', flat=True)
        if existing_labels:
            msg = f'Labels with these ids already exist: {list(existing_labels)}'
            raise serializers.ValidationError({'labels': msg})

    @staticmethod
    def create_labels(annotation, labels_data):
        if labels_data:
            for label in labels_data:
                label['annotation_id'] = annotation.id

            serializer = LabelSerializer(data=labels_data, many=True)

            serializer.is_valid(raise_exception=True)
            AnnotationSerializer.check_existing_labels(serializer.validated_data)

            labels = serializer.save()
        else:
            labels = []
        return labels

    @transaction.atomic
    def create(self, validated_data):
        labels_data = validated_data.pop('labels', None)
        annotation = super().create(validated_data)

        self.create_labels(annotation, labels_data)

        return annotation

    @transaction.atomic
    def update(self, instance, validated_data):
        labels_data = validated_data.pop('labels', None)
        instance = super().update(instance, validated_data)

        instance.labels.all().delete()
        self.create_labels(instance, labels_data)

        return instance


class ImageSerializer(serializers.ModelSerializer):
    SUPPORTED_FORMATS = ['JPEG', 'PNG', 'TIFF']
    FILE_MAX_SIZE = 20 * 1024 * 1024  # in MB

    annotation = AnnotationSerializer(required=False)

    class Meta:
        model = Image
        fields = ['file', 'annotation']

    def to_internal_value(self, data: dict):
        data = dict(data)
        for key, val in data.items():
            if val:
                data[key] = val[0]  # unpack data from multipart format

        return super().to_internal_value(data)

    def to_representation(self, instance):
        return {'id': instance.file.name}

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

from django.utils.text import get_valid_filename
from rest_framework import serializers

from core.models import Image


class ImagesSerializer(serializers.ModelSerializer):
    SUPPORTED_FORMATS = ['JPEG', 'PNG', 'TIFF']
    FILE_MAX_SIZE = 20 * 1024 * 1024  # in MB

    class Meta:
        model = Image
        fields = ['file']

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
        super().to_representation(instance)
        return {'id': instance.file.name}

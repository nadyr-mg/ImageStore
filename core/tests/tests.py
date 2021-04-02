import json
import os
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from django.forms import model_to_dict
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Image, Annotation
from core.serializers import ImageSerializer

TEST_DIR = Path(__file__).resolve().parent


class CommonTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.client = APIClient()

        self.valid_image_path = TEST_DIR.joinpath('sample.png')
        self.invalid_image_path = TEST_DIR.joinpath('sample.gif')

        self.valid_annotation = {
            "labels": [
                {
                    "id": "2b1cd508-587b-493b-98ea-b08a8c31d111",
                    "class_id": "tooth",
                    "surface": [
                        "1",
                        "2",
                        "3"
                    ],
                    "shape": {
                        "endX": 111,
                        "endY": 1399,
                        "startY": 605,
                        "startX": 44
                    },
                    "meta": {
                        "confirmed": True,
                        "confidence_percent": 0.99
                    }
                }
            ]
        }

    def upload_image(self, path, include_annotation=True):
        with open(path, 'rb') as fp:
            data = {
                'file': fp,
                'data': json.dumps({'annotation': self.valid_annotation}) if include_annotation else ''
            }
            response = self.client.post(reverse('images-create'), data, format='multipart')
            return response


class ImageCreationTestCase(CommonTestCase):
    def test_create_valid(self):
        response = self.upload_image(self.valid_image_path)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        file_id = response.json()['id']
        try:
            image = Image.objects.get(file=file_id)
            self.assertEquals(image.file.size, os.path.getsize(self.valid_image_path))

            annotation = Annotation.objects.get(image__id=image.id)

            label = list(annotation.labels.all())[0]
            compare_data = model_to_dict(label)
            compare_data['id'] = str(label.id)
            compare_data.pop('annotation')
            self.assertDictEqual(compare_data, self.valid_annotation['labels'][0])
        except (Image.DoesNotExist, Annotation.DoesNotExist) as err:
            self.fail(err)

    def test_create_no_annotation_valid(self):
        response = self.upload_image(self.valid_image_path, include_annotation=False)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        file_id = response.json()['id']
        try:
            image = Image.objects.get(file=file_id)
            self.assertEquals(image.file.size, os.path.getsize(self.valid_image_path))
        except Image.DoesNotExist as err:
            self.fail(err)

        with self.assertRaises(Annotation.DoesNotExist):
            Annotation.objects.get(image__id=image.id)

    def test_create_wrong_format(self):
        response = self.upload_image(self.invalid_image_path)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected = {'file': [f"GIF format is not supported. Supported formats: {ImageSerializer.SUPPORTED_FORMATS}"]}
        self.assertDictEqual(response.json(), expected)

    def test_create_big_image(self):
        size = os.path.getsize(self.valid_image_path)
        with patch('core.serializers.ImageSerializer.FILE_MAX_SIZE', size - 1):
            response = self.upload_image(self.valid_image_path)
            self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

            expected = {'file': [f'Your file is too big. Maximum size is {ImageSerializer.FILE_MAX_SIZE} MB']}
            self.assertDictEqual(response.json(), expected)


class ImageRetrieveTestCase(CommonTestCase):
    def test_retrieve_valid(self):
        response = self.upload_image(self.valid_image_path)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        file_id = response.json()['id']

        response = self.client.get(reverse('images-retrieve', kwargs={'file': file_id}))

        self.assertEquals(int(response.get('Content-Length')), os.path.getsize(self.valid_image_path))
        self.assertEquals(response.get('Content-Disposition'), f'attachment; filename="{file_id}"')

    def test_retrieve_404(self):
        response = self.client.get(reverse('images-retrieve', kwargs={'file': 'sdfsd.jpg'}))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)


class AnnotationBaseTestCase(CommonTestCase):
    def setUp(self) -> None:
        super().setUp()

        response = self.upload_image(self.valid_image_path)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        self.file_id = response.json()['id']


class AnnotationUpdateTestCase(AnnotationBaseTestCase):
    def test_update_valid(self):
        data = {
            "labels": [
                {
                    "id": "1b1cd508-587b-493b-98ea-b11a8c31d111",
                    "class_id": "tooth",
                    "surface": [
                        "5",
                        "6",
                        "9"
                    ],
                    "shape": {
                        "endX": 111,
                        "endY": 92,
                        "startY": 605,
                        "startX": 44
                    },
                    "meta": {
                        "confirmed": False,
                        "confidence_percent": 0.99
                    }
                }
            ]
        }
        response = self.client.put(reverse('annotation', kwargs={'image__file': self.file_id}), json.dumps(data),
                                   content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        label = Annotation.objects.get(image__file=self.file_id).labels.first()

        compare_data = model_to_dict(label)
        compare_data['id'] = str(label.id)
        compare_data.pop('annotation')
        self.assertDictEqual(compare_data, data['labels'][0])

    def test_update_empty_valid(self):
        data = {
            "labels": []
        }
        response = self.client.put(reverse('annotation', kwargs={'image__file': self.file_id}), json.dumps(data),
                                   content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        label = Annotation.objects.get(image__file=self.file_id).labels.first()
        self.assertIsNone(label)

    def test_update_invalid(self):
        data = {
            "labels": [
                {}  # empty label is invalid
            ]
        }
        response = self.client.put(reverse('annotation', kwargs={'image__file': self.file_id}), json.dumps(data),
                                   content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)


class AnnotationRetrieveTestCase(CommonTestCase):
    def setUp(self) -> None:
        super().setUp()

        first_label = deepcopy(self.valid_annotation['labels'][0])
        first_label['id'] = "1a3cd508-587b-493b-98ea-b08a8c31d111"
        first_label['meta']['confirmed'] = False
        self.valid_annotation['labels'].append(first_label)

        response = self.upload_image(self.valid_image_path)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        self.file_id = response.json()['id']

    def test_retrieve_internal_valid(self):
        response = self.client.get(reverse('annotation', kwargs={'image__file': self.file_id}), dict(format='internal'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        self.assertDictEqual(response.json(), self.valid_annotation)

    def test_retrieve_export_valid(self):
        response = self.client.get(reverse('annotation', kwargs={'image__file': self.file_id}), dict(format='export'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        expected = {
            "labels": [
                {
                    "id": "2b1cd508-587b-493b-98ea-b08a8c31d111",
                    "class_id": "tooth",
                    "surface": "123",
                }
            ]
        }
        self.assertDictEqual(response.json(), expected)

import uuid

from django.db import models


class Image(models.Model):
    file = models.ImageField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


# this model seems redundant, but it allows us to easily extend annotation fields if it'll be needed
class Annotation(models.Model):
    image = models.OneToOneField(Image, on_delete=models.CASCADE)

    def __str__(self):
        return f'Annotation #{self.image_id}'


class Label(models.Model):
    annotation = models.ForeignKey(Annotation, related_name='labels', on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    class_id = models.CharField(max_length=255)
    surface = models.JSONField(blank=True, default=list)
    shape = models.JSONField(blank=True, default=dict)
    meta = models.JSONField(blank=True, default=dict)

    def __str__(self):
        return f'{self.id}: {self.class_id}'

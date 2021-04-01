from django.contrib import admin

# Register your models here.
from core.models import *

admin.site.register(Image)
admin.site.register(Annotation)
admin.site.register(Label)

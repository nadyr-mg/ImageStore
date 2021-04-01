from django.urls import path

from core.views import ImagesView

urlpatterns = [
    path('v1/images/', ImagesView.as_view({'post': 'create'}), name='images'),
]

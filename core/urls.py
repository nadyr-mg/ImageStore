from django.urls import path

from core.views import ImageView

urlpatterns = [
    path('v1/images/', ImageView.as_view({'post': 'create'}), name='images'),
]

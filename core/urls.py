from django.urls import path

from core.views import ImageView, AnnotationView

urlpatterns = [
    path('v1/images/', ImageView.as_view({'post': 'create'}), name='images-create'),
    path('v1/images/<str:file>/', ImageView.as_view({'get': 'retrieve'}), name='images-retrieve'),
    path('v1/images/<str:image__file>/annotation/', AnnotationView.as_view(), name='annotation'),
]

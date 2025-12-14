from django.urls import path
from .views import (
    YOLODetectionView,
    ImageUploadView,
    health_check
)

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('detect/', YOLODetectionView.as_view(), name='yolo-detect'),
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
]
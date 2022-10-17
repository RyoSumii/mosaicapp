from django.urls import path
from . import views
urlpatterns = [
    path('', views.mosaic_image, name='mosaic_image'),
]
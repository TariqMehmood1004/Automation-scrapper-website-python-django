from . import views
from django.urls import path

urlpatterns = [
    path('', views.INDEX, name='index'),
    path('checkout/', views.CREATE_ORDER, name='create-order'),
]
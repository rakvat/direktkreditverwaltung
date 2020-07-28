from django.urls import path

from . import views

app_name = 'dkapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('contacts/', views.contacts, name='contacts'),
    path('contacts/<int:contact_id>/', views.contact, name='contact'),
]

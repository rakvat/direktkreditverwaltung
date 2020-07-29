from django.urls import path

from . import views

app_name = 'dkapp'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('contacts/<int:pk>/', views.ContactView.as_view(), name='contact'),
    path('contacts/new/', views.contact2, name='contact2'),
]

from django.urls import path

from . import views

app_name = 'dkapp'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('contacts/new/', views.ContactsView.new, name='contacts_new'),
    path('contacts/<int:pk>/', views.ContactView.as_view(), name='contact'),
    path('contacts/<int:pk>/edit', views.ContactView.edit, name='contact_edit'),
    path('contacts/<int:pk>/delete', views.ContactDeleteView.as_view(), name='contact_delete'),

    path('contracts/', views.ContractsView.as_view(), name='contracts'),
    path('contracts_interest/', views.ContractsView.interest, name='contracts_interest'),
    path('contracts_interest_transfer_list/', views.ContractsView.interest_transfer_list, name='contracts_interest_transfer_list'),
    path('contracts_interest_average/', views.ContractsView.interest_average, name='contracts_interest_average'),
    path('contracts_expiring/', views.ContractsView.expiring, name='contracts_expiring'),

    path('contract_versions/', views.ContractVersionsView.as_view(), name='contract_versions'),

    path('accounting_entries/', views.AccountingEntriesView.as_view(), name='accounting_entries'),
]

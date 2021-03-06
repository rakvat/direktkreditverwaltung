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

    path('contracts', views.ContractsView.as_view(), name='contracts'),
    path('contracts/new/', views.ContractsView.new, name='contracts_new'),
    path('contracts/<int:pk>/', views.ContractView.as_view(), name='contract'),
    path('contracts/<int:pk>/edit', views.ContractView.edit, name='contract_edit'),
    path('contracts/<int:pk>/delete', views.ContractDeleteView.as_view(), name='contract_delete'),
    path('contracts/<int:pk>/version_new', views.ContractVersionsView.new, name='contract_version_new'),
    path('contracts/<int:pk>/accounting_entry_new', views.AccountingEntriesView.new, name='contract_accounting_entry_new'),

    path('contracts_interest/', views.ContractsInterest.as_view(), name='contracts_interest'),
    path('contracts_interest/filter', views.ContractsInterest.filter, name='contracts_interest_filter'),
    path('contracts_interest_transfer_list/', views.ContractsInterestTransferListView.as_view(), name='contracts_interest_transfer_list'),
    path('contracts_interest_average/', views.ContractsAverageInterestView.as_view(), name='contracts_interest_average'),
    path('contracts_expiring/', views.ContractsExpiringView.as_view(), name='contracts_expiring'),
    path('contracts_remaining/', views.ContractsRemainingView.as_view(), name='contracts_remaining'),

    path('contract_versions/', views.ContractVersionsView.as_view(), name='contract_versions'),
    path('contract_versions/<int:pk>/', views.ContractVersionView.as_view(), name='contract_version'),
    path('contract_versions/<int:pk>/edit', views.ContractVersionView.edit, name='contract_version_edit'),
    path('contract_versions/<int:pk>/delete', views.ContractVersionDeleteView.as_view(), name='contract_version_delete'),

    path('accounting_entries/', views.AccountingEntriesView.as_view(), name='accounting_entries'),
    path('accounting_entries/filter', views.AccountingEntriesView.filter, name='accounting_entries_filter'),
    path('accounting_entries/<int:pk>', views.AccountingEntryView.as_view(), name='accounting_entry'),
    path('accounting_entries/<int:pk>/edit', views.AccountingEntryView.edit, name='accounting_entry_edit'),
    path('accounting_entries/<int:pk>/delete', views.AccountingEntryDeleteView.as_view(), name='accounting_entry_delete'),
]

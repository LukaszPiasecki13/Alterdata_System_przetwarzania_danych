from django.urls import path, include
from . import views


urlpatterns = [
    path('transactions/upload',views.TransactionUploadView.as_view(), name='transaction-upload'),
    path('transactions/', views.TransactionListView.as_view(), name = 'transaction-list'),
    path('transactions/<uuid:transaction_id>/', views.TransactionDetailView.as_view(), name = 'transaction-detail'),
]
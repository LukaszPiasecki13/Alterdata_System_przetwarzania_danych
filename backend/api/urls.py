from django.urls import path, include
from . import views


urlpatterns = [
    path('transactions/upload',views.TransactionUploadView.as_view(), name='transactions-upload'),
    path('transactions/', views.TransactionListView.as_view(), name = 'transactions-list'),
    path('transactions/<uuid:transaction_id>/', views.TransactionDetailView.as_view(), name = 'transactions-detail'),
    path('tasks/<str:task_id>/', views.TaskStatusView.as_view(), name='task-status'),
]
from django.urls import path, include
from . import views


urlpatterns = [
    path('transactions/upload',views.TransactionView.as_view(), name='transaction-upload'),
]
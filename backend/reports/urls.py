from django.urls import path, include
from . import views


urlpatterns = [
    path('customer-summary/<uuid:customer_id>/', views.CustomerSummaryView.as_view(), name='customer-summary'),
    path('product-summary/<uuid:product_id>/', views.ProductSummaryView.as_view(), name='product-summary'),
]
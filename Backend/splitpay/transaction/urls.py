from django.contrib import admin
from django.urls import path,include
from  . import views

urlpatterns = [
    path('payment/', views.payment, name="payment"),
    path('splitpayment/', views.splitpayment, name="splitpayment"),
    path('frequentcontacts/', views.frequentcontacts, name="frequentcontacts"),
    path('recenttransaction/', views.recenttransaction, name="recenttransaction"),
    path('splits/', views.splits, name="splits"),
    path('split/<str:pk>/', views.split, name="split"),
    path('settleup/<str:pk>/', views.settleup, name="settleup"),

    # Checking
    path('allpayment/', views.allpayment, name="allpayment"),
    path('alldebt/', views.alldebt, name="alldebt"),
]
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('setup/', views.setup_view, name='setup'),
    path('', views.rating_view, name='rating'),
    path('reason/<str:rating>/', views.reason_view, name='reason'),
    path('submit/', views.submit_response, name='submit'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
]

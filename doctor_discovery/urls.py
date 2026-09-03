from django.urls import path
from .views.telehealth import (
    directory_view,
    doctor_detail_view,
    book_appointment_view,
    doctor_dashboard_view,
    telehealth_room_view,
    patient_appointments_view
)

app_name = 'telehealth'

urlpatterns = [
    path('', directory_view, name='directory'),
    path('doctor/<int:pk>/', doctor_detail_view, name='doctor_detail'),
    path('doctor/<int:doctor_id>/book/', book_appointment_view, name='book_appointment'),
    path('dashboard/', doctor_dashboard_view, name='doctor_dashboard'),
    path('appointments/', patient_appointments_view, name='patient_appointments'),
    path('room/<int:appointment_id>/', telehealth_room_view, name='room'),
]

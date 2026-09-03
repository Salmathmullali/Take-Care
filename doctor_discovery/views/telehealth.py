from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from doctor_discovery.models import DoctorProfile, DoctorAvailability, Appointment, Specialization, Hospital
from datetime import datetime, timedelta

def directory_view(request):
    specializations = Specialization.objects.all()
    doctors = DoctorProfile.objects.all()
    
    specialty_id = request.GET.get('specialty')
    if specialty_id:
        doctors = doctors.filter(specializations__id=specialty_id)
        
    context = {
        'doctors': doctors,
        'specializations': specializations,
    }
    return render(request, 'doctor_discovery/directory.html', context)

def doctor_detail_view(request, pk):
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    availabilities = doctor.availabilities.all().order_by('day_of_week', 'start_time')
    
    # Simple logic for next available slots (just passing availabilities for now)
    context = {
        'doctor': doctor,
        'availabilities': availabilities,
    }
    return render(request, 'doctor_discovery/doctor_detail.html', context)

@login_required
def book_appointment_view(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
    if request.method == 'POST':
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        
        if date_str and time_str:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            time_obj = datetime.strptime(time_str, '%H:%M').time()
            
            Appointment.objects.create(
                patient=request.user,
                doctor=doctor,
                date=date_obj,
                time=time_obj,
                status='Confirmed'
            )
            messages.success(request, 'Appointment booked successfully!')
            return redirect('telehealth:patient_appointments')
        else:
            messages.error(request, 'Please select both date and time.')
            
    # For GET, render booking form
    return render(request, 'doctor_discovery/booking.html', {'doctor': doctor})

@login_required
def doctor_dashboard_view(request):
    # Ensure user is a doctor
    if request.user.user_type != 4: # DOCTOR
        messages.error(request, 'Unauthorized access.')
        return redirect('/')
        
    try:
        profile = request.user.doctor_profile
    except DoctorProfile.DoesNotExist:
        profile = DoctorProfile.objects.create(user=request.user)
        
    appointments = Appointment.objects.filter(doctor=profile).order_by('date', 'time')
    availabilities = DoctorAvailability.objects.filter(doctor=profile)
    
    if request.method == 'POST':
        # Add availability logic
        day = request.POST.get('day_of_week')
        start = request.POST.get('start_time')
        end = request.POST.get('end_time')
        if day and start and end:
            DoctorAvailability.objects.create(
                doctor=profile,
                day_of_week=day,
                start_time=start,
                end_time=end
            )
            messages.success(request, 'Availability added.')
            return redirect('telehealth:doctor_dashboard')
            
    context = {
        'profile': profile,
        'appointments': appointments,
        'availabilities': availabilities,
        'days': DoctorAvailability.DAYS_OF_WEEK,
    }
    return render(request, 'doctor_discovery/dashboard.html', context)

@login_required
def patient_appointments_view(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('date', 'time')
    return render(request, 'doctor_discovery/patient_appointments.html', {'appointments': appointments})

@login_required
def telehealth_room_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    
    # Allow if user is either the patient or the doctor of this appointment
    if request.user != appointment.patient and request.user != appointment.doctor.user:
        messages.error(request, 'You do not have permission to join this call.')
        return redirect('/')
        
    context = {
        'appointment': appointment,
        'room_id': appointment.room_id,
        'user_name': f"{request.user.first_name} {request.user.last_name}",
        'is_doctor': request.user == appointment.doctor.user
    }
    return render(request, 'doctor_discovery/telehealth_room.html', context)

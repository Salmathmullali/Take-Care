from django.urls import include, path

from charity.views import dashboard, hub, messages
from charity.views.admin import views as admin_views
from charity.views.blood import views as blood_views
from charity.views.food import views as food_views
from charity.views.medical import views as medical_views

app_name = 'charity'

urlpatterns = [
    path('', hub.hub, name='hub'),
    path('dashboard/', dashboard.my_dashboard, name='my_dashboard'),
    path(
        'messages/<str:pillar>/<int:pk>/',
        messages.connection_messages,
        name='messages',
    ),
    path('blood/', include((
        [
            path('', blood_views.blood_hub, name='hub'),
            path('apply/donor/', blood_views.apply_donor, name='apply_donor'),
            path('apply/requester/', blood_views.apply_requester, name='apply_requester'),
            path('browse/donors/', blood_views.browse_donors, name='browse_donors'),
            path('browse/requesters/', blood_views.browse_requesters, name='browse_requesters'),
            path('request/<int:donor_id>/', blood_views.send_request, name='send_request'),
            path('match/<int:pk>/', blood_views.match_detail, name='match_detail'),
        ],
        'blood',
    ), namespace='blood')),
    path('medical-bills/', include((
        [
            path('', medical_views.medical_hub, name='hub'),
            path('apply/recipient/', medical_views.apply_recipient, name='apply_recipient'),
            path('apply/sponsor/', medical_views.apply_sponsor, name='apply_sponsor'),
            path('browse/', medical_views.browse_needs, name='browse_needs'),
            path('need/<int:pk>/', medical_views.recipient_detail, name='recipient_detail'),
            path('offer/<int:recipient_id>/', medical_views.send_offer, name='send_offer'),
            path('match/<int:pk>/', medical_views.match_detail, name='match_detail'),
        ],
        'medical',
    ), namespace='medical')),
    path('food/', include((
        [
            path('', food_views.food_hub, name='hub'),
            path('apply/supplier/', food_views.apply_supplier, name='apply_supplier'),
            path('apply/distributor/', food_views.apply_distributor, name='apply_distributor'),
            path('listing/new/', food_views.create_listing, name='create_listing'),
            path('browse/', food_views.browse_listings, name='browse'),
            path('claim/<int:listing_id>/', food_views.claim_listing, name='claim'),
            path('pickup/<int:pk>/', food_views.pickup_detail, name='pickup_detail'),
        ],
        'food',
    ), namespace='food')),
    path('review/', include((
        [
            path('', admin_views.review_dashboard, name='dashboard'),
            path('<str:profile_type>/<int:pk>/', admin_views.review_detail, name='detail'),
            path('<str:profile_type>/<int:pk>/accept/', admin_views.review_accept, name='accept'),
            path('<str:profile_type>/<int:pk>/reject/', admin_views.review_reject, name='reject'),
        ],
        'admin',
    ), namespace='admin')),
]

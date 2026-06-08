from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.role_selection_view, name='role_selection'),
    path('login/<str:role>/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('my-loans/', views.my_loans_view, name='my_loans'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('profile/', views.profile_view, name='profile'),
    
    # Leader URLs
    path('leader/home/', views.leader_home_view, name='leader_home'),
    path('leader/meeting-alert/', views.leader_meeting_alert_view, name='leader_meeting_alert'),
    path('leader/members/', views.leader_members_list_view, name='leader_members_list'),
    
    # Admin URLs
    path('admin-dashboard/home/', views.admin_home_view, name='admin_home'),
    path('admin-dashboard/group-loans/', views.admin_group_loans_view, name='admin_group_loans'),
    path('admin-dashboard/group-details/<int:group_id>/', views.admin_group_details_view, name='admin_group_details'),
    path('admin-dashboard/member-loan/<int:member_id>/', views.admin_member_loan_details_view, name='admin_member_loan_details'),
    path('admin-dashboard/notifications/', views.admin_notifications_view, name='admin_notifications'),
    path('admin-dashboard/profile/', views.admin_profile_view, name='admin_profile'),
]

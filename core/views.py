from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages

def role_selection_view(request):
    return render(request, 'core/login_role_selection.html')

def get_base_template(request):
    try:
        if request.user.is_authenticated:
            role = request.user.userprofile.role
            if role == 'leader':
                return 'core/base_leader_dashboard.html'
            elif role == 'admin':
                return 'core/base_admin_dashboard.html'
    except Exception:
        pass
    return 'core/base_dashboard.html'

from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from .models import UserProfile, MemberProfile, SHGGroup

def login_view(request, role):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        otp = request.POST.get('otp')
        try:
            user = User.objects.get(username=phone)
            if not hasattr(user, 'userprofile') or user.userprofile.role != role:
                messages.error(request, f"This phone number is not registered as a {role.title()}.")
                return render(request, 'core/login.html', {'role': role})
            
            if not user.check_password(otp):
                messages.error(request, "Invalid OTP.")
                return render(request, 'core/login.html', {'role': role})

            auth_login(request, user)
            if role == 'member':
                return redirect('core:home')
            elif role == 'leader':
                return redirect('core:leader_home')
            elif role == 'admin':
                return redirect('core:admin_home')
                
        except User.DoesNotExist:
            messages.error(request, "Phone number not registered.")
            return render(request, 'core/login.html', {'role': role})
            
    return render(request, 'core/login.html', {'role': role})

@login_required
def home_view(request):
    try:
        member = request.user.memberprofile
        active_loan = member.loans.filter(status='active').first()
        my_contribution = member.savings.aggregate(Sum('amount'))['amount__sum'] or 0
        
        current_due_amount = 0
        current_due_date = None
        loan_remaining = 0
        due_status = 'No Dues'
        
        if active_loan:
            pending_emis = active_loan.emis.filter(is_paid=False).order_by('due_date')
            if pending_emis.exists():
                next_emi = pending_emis.first()
                current_due_amount = next_emi.amount
                current_due_date = next_emi.due_date
                due_status = 'Pending'
            loan_remaining = pending_emis.aggregate(Sum('amount'))['amount__sum'] or 0
            
        context = {
            'member': member,
            'current_due_amount': current_due_amount,
            'current_due_date': current_due_date,
            'due_status': due_status,
            'loan_remaining': loan_remaining,
            'my_contribution': my_contribution,
        }
    except Exception as e:
        context = {}
    return render(request, 'core/home.html', context)

@login_required
def my_loans_view(request):
    try:
        member = request.user.memberprofile
        active_loan = member.loans.filter(status='active').first()
        completed_loans = member.loans.filter(status='completed')
        
        # Savings
        savings = member.savings.all().order_by('-month')
        total_savings = member.savings.aggregate(Sum('amount'))['amount__sum'] or 0
        months_contributed = member.savings.count()
        interest_earned = float(total_savings) * 0.05 if total_savings else 0
        withdrawable_amount = float(total_savings) + interest_earned
        
        amount_paid = 0
        remaining_balance = 0
        monthly_installment = 0
        next_due_date = None
        last_payment_date = None
        
        if active_loan:
            paid_emis = active_loan.emis.filter(is_paid=True).order_by('-paid_date')
            pending_emis = active_loan.emis.filter(is_paid=False).order_by('due_date')
            amount_paid = paid_emis.aggregate(Sum('amount'))['amount__sum'] or 0
            remaining_balance = pending_emis.aggregate(Sum('amount'))['amount__sum'] or 0
            if active_loan.emis.exists():
                monthly_installment = active_loan.emis.first().amount
            if paid_emis.exists():
                last_payment_date = paid_emis.first().paid_date
            if pending_emis.exists():
                next_due_date = pending_emis.first().due_date
                
        context = {
            'active_loan': active_loan,
            'completed_loans': completed_loans,
            'amount_paid': amount_paid,
            'remaining_balance': remaining_balance,
            'monthly_installment': monthly_installment,
            'next_due_date': next_due_date,
            'last_payment_date': last_payment_date,
            'savings': savings,
            'total_savings': total_savings,
            'months_contributed': months_contributed,
            'interest_earned': interest_earned,
            'withdrawable_amount': withdrawable_amount,
            'base_template': get_base_template(request),
        }
    except Exception as e:
        context = {}
    return render(request, 'core/my_loans.html', context)

@login_required
def notifications_view(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    context = {
        'notifications': notifications,
        'base_template': get_base_template(request),
    }
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', context)

@login_required
def profile_view(request):
    try:
        member = request.user.memberprofile
        leader = member.shg_group.members.filter(is_leader=True).first()
        context = {
            'member': member,
            'leader': leader,
            'base_template': get_base_template(request),
        }
    except Exception:
        context = {}
    return render(request, 'core/profile.html', context)

@login_required
def leader_home_view(request):
    try:
        member = request.user.memberprofile
        active_loan = member.loans.filter(status='active').first()
        my_contribution = member.savings.aggregate(Sum('amount'))['amount__sum'] or 0
        
        current_due_amount = 0
        current_due_date = None
        loan_remaining = 0
        due_status = 'No Dues'
        
        if active_loan:
            pending_emis = active_loan.emis.filter(is_paid=False).order_by('due_date')
            if pending_emis.exists():
                next_emi = pending_emis.first()
                current_due_amount = next_emi.amount
                current_due_date = next_emi.due_date
                due_status = 'Pending'
            loan_remaining = pending_emis.aggregate(Sum('amount'))['amount__sum'] or 0
            
        context = {
            'member': member,
            'current_due_amount': current_due_amount,
            'current_due_date': current_due_date,
            'due_status': due_status,
            'loan_remaining': loan_remaining,
            'my_contribution': my_contribution,
        }
    except Exception as e:
        context = {}
    return render(request, 'core/leader_home.html', context)

@login_required
def leader_meeting_alert_view(request):
    member = request.user.memberprofile
    if request.method == 'POST':
        title = request.POST.get('title')
        date = request.POST.get('date')
        time = request.POST.get('time')
        message = request.POST.get('message')
        
        from .models import MeetingAlert, Notification
        alert = MeetingAlert.objects.create(
            shg_group=member.shg_group,
            title=title,
            meeting_date=date,
            meeting_time=time,
            message=message,
            created_by=request.user
        )
        
        # Notify all members in the group
        for group_member in member.shg_group.members.all():
            Notification.objects.create(
                user=group_member.user,
                title="Upcoming SHG Meeting",
                message=f"Alert: {title} scheduled on {date} at {time}. {message}",
                icon_type='calendar'
            )
            
        messages.success(request, "Meeting alert sent to all members successfully!")
        return redirect('core:leader_home')
        
    return render(request, 'core/meeting_alert.html', {'member': member})

@login_required
def leader_members_list_view(request):
    member = request.user.memberprofile
    members = member.shg_group.members.all()
    
    # Calculate loan status for each member
    members_data = []
    for m in members:
        has_active = m.loans.filter(status='active').exists()
        members_data.append({
            'profile': m,
            'has_active_loan': has_active,
        })
        
    context = {
        'member': member,
        'members_data': members_data
    }
    return render(request, 'core/members_list.html', context)

# ADMIN VIEWS
@login_required
def admin_home_view(request):
    groups = SHGGroup.objects.all()
    group_data = []
    for g in groups:
        total = 0
        outstanding = 0
        for m in g.members.all():
            for l in m.loans.all():
                total += float(l.total_payable)
                outstanding += float(l.emis.filter(is_paid=False).aggregate(Sum('amount'))['amount__sum'] or 0)
        group_data.append({'group': g, 'total': total, 'outstanding': outstanding, 'member_count': g.members.count()})
    return render(request, 'core/admin_home.html', {'group_data': group_data})

@login_required
def admin_group_loans_view(request):
    groups = SHGGroup.objects.all()
    group_data = []
    for g in groups:
        total = 0
        outstanding = 0
        for m in g.members.all():
            for l in m.loans.all():
                total += float(l.total_payable)
                outstanding += float(l.emis.filter(is_paid=False).aggregate(Sum('amount'))['amount__sum'] or 0)
        group_data.append({'group': g, 'total': total, 'outstanding': outstanding, 'member_count': g.members.count()})
    return render(request, 'core/admin_group_loans.html', {'group_data': group_data})

@login_required
def admin_group_details_view(request, group_id):
    group = get_object_or_404(SHGGroup, id=group_id)
    total = 0
    outstanding = 0
    members_data = []
    for m in group.members.all():
        m_total = 0
        m_out = 0
        has_active = False
        for l in m.loans.all():
            m_total += float(l.total_payable)
            m_out += float(l.emis.filter(is_paid=False).aggregate(Sum('amount'))['amount__sum'] or 0)
            if l.status == 'active': has_active = True
        total += m_total
        outstanding += m_out
        members_data.append({'member': m, 'has_active': has_active})
        
    context = {
        'group': group,
        'total': total,
        'outstanding': outstanding,
        'members_data': members_data
    }
    return render(request, 'core/admin_group_details.html', context)

@login_required
def admin_member_loan_details_view(request, member_id):
    member = get_object_or_404(MemberProfile, id=member_id)
    active_loan = member.loans.filter(status='active').first()
    
    if request.method == 'POST':
        emi_id = request.POST.get('emi_id')
        if emi_id:
            from .models import LoanEMI, Notification
            emi = LoanEMI.objects.get(id=emi_id)
            emi.is_paid = True
            from django.utils import timezone
            emi.paid_date = timezone.now().date()
            emi.save()
            
            # Send Notification
            msg = f"Installment of ₹{emi.amount} marked as paid for Loan ID #{emi.loan.id}."
            Notification.objects.create(user=member.user, title="Loan Repayment", message=msg, icon_type='wallet')
            
            leader = member.shg_group.members.filter(is_leader=True).first()
            if leader and leader != member:
                Notification.objects.create(user=leader.user, title="Member Repayment Update", message=f"{member.user.get_full_name() or member.user.username} paid ₹{emi.amount}.", icon_type='wallet')
                
            messages.success(request, f"EMI of ₹{emi.amount} marked as paid successfully.")
                
        return redirect('core:admin_member_loan_details', member_id=member.id)
        
    amount_paid = 0
    remaining_balance = 0
    if active_loan:
        amount_paid = active_loan.emis.filter(is_paid=True).aggregate(Sum('amount'))['amount__sum'] or 0
        remaining_balance = active_loan.emis.filter(is_paid=False).aggregate(Sum('amount'))['amount__sum'] or 0
        
    context = {
        'member': member,
        'active_loan': active_loan,
        'amount_paid': amount_paid,
        'remaining_balance': remaining_balance
    }
    return render(request, 'core/admin_member_loan_details.html', context)

@login_required
def admin_notifications_view(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    context = {
        'notifications': notifications,
        'base_template': get_base_template(request),
    }
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', context)

@login_required
def admin_profile_view(request):
    return render(request, 'core/admin_profile.html')

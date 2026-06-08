import os
import django
from datetime import date, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shg_smartledger.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, MemberProfile, SHGGroup, Loan, LoanEMI, Savings, Notification, MeetingAlert

def seed():
    print("Clearing old data...")
    User.objects.exclude(is_superuser=True).delete()
    SHGGroup.objects.all().delete()
    
    print("Creating SHG Groups...")
    group1 = SHGGroup.objects.create(name="Yashoda Mahila Sangham", village="Sangam", formed_date=date(2022, 5, 10))
    group2 = SHGGroup.objects.create(name="Sai Lakshmi SHG", village="Tirupati Rural", formed_date=date(2023, 8, 15))
    group3 = SHGGroup.objects.create(name="Durga Bhavani SHG", village="Chandragiri", formed_date=date(2024, 1, 20))
    
    print("Creating Admin User...")
    admin_user = User.objects.create_user(username="9951458910", password="123", first_name="Kavitha", last_name="R")
    UserProfile.objects.create(user=admin_user, role='admin')
    
    print("Creating Leader Users...")
    l1_user = User.objects.create_user(username="9951458911", password="123", first_name="Pavani", last_name="M")
    UserProfile.objects.create(user=l1_user, role='leader')
    l1 = MemberProfile.objects.create(
        user=l1_user, shg_group=group1, phone="9951458911", is_leader=True, 
        member_id="SHG1001", bank_name="State Bank of India", account_no="23345899011", ifsc_code="SBIN0001234"
    )

    l2_user = User.objects.create_user(username="9951458912", password="123", first_name="Saranya", last_name="V")
    UserProfile.objects.create(user=l2_user, role='leader')
    MemberProfile.objects.create(
        user=l2_user, shg_group=group2, phone="9951458912", is_leader=True,
        member_id="SHG2001", bank_name="Andhra Bank", account_no="012345678912", ifsc_code="ANDB0000123"
    )

    l3_user = User.objects.create_user(username="9951458913", password="123", first_name="Bhavani", last_name="J")
    UserProfile.objects.create(user=l3_user, role='leader')
    MemberProfile.objects.create(
        user=l3_user, shg_group=group3, phone="9951458913", is_leader=True,
        member_id="SHG3001", bank_name="Bank of Baroda", account_no="987654321098", ifsc_code="BARB0TIRUPA"
    )
    
    print("Creating Member Users for Group 1...")
    g1_names = [("Shravya", "Rupani", "9951458919"), ("Lakshmi", "P", "9951458920"), ("Radhika", "K", "9951458921"), ("Reshma", "Begum", "9951458922"), ("Lohitha", "B", "9951458923")]
    g1_members = []
    for i, (fn, ln, phone) in enumerate(g1_names):
        u = User.objects.create_user(username=phone, password="123", first_name=fn, last_name=ln)
        UserProfile.objects.create(user=u, role='member')
        m = MemberProfile.objects.create(user=u, shg_group=group1, phone=phone, is_leader=False, member_id=f"SHG102{i+3}", bank_name="Union Bank", account_no=f"456789{i}12340", ifsc_code="UBIN0805123")
        g1_members.append(m)

    print("Creating Member Users for Group 2...")
    g2_names = [("Geetha", "S", "9951458924"), ("Anusha", "M", "9951458925"), ("Swathi", "T", "9951458926"), ("Roopa", "L", "9951458927"), ("Madhavi", "R", "9951458928")]
    for i, (fn, ln, phone) in enumerate(g2_names):
        u = User.objects.create_user(username=phone, password="123", first_name=fn, last_name=ln)
        UserProfile.objects.create(user=u, role='member')
        MemberProfile.objects.create(user=u, shg_group=group2, phone=phone, is_leader=False, member_id=f"SHG202{i+3}")

    print("Creating Member Users for Group 3...")
    g3_names = [("Padma", "K", "9951458929"), ("Nadiya", "S", "9951458930"), ("Bhargavi", "Y", "9951458931"), ("Sindhu", "N", "9951458932"), ("Pooja", "C", "9951458933")]
    for i, (fn, ln, phone) in enumerate(g3_names):
        u = User.objects.create_user(username=phone, password="123", first_name=fn, last_name=ln)
        UserProfile.objects.create(user=u, role='member')
        MemberProfile.objects.create(user=u, shg_group=group3, phone=phone, is_leader=False, member_id=f"SHG302{i+3}")

    
    print("Adding Loans and EMIs...")
    m1 = g1_members[0] # Shravya
    
    # Active Loan for Shravya (Member 1)
    loan1 = Loan.objects.create(
        member=m1,
        principal_amount=20000,
        interest_rate=12.0,
        duration_months=12,
        start_date=date(2025, 4, 10),
        status='active'
    )
    emi_amount1 = loan1.total_payable / loan1.duration_months
    for i in range(12):
        is_paid = i < 4
        due = date(2025 + ((4+i)//12), ((4+i)%12)+1, 10)
        LoanEMI.objects.create(
            loan=loan1,
            amount=emi_amount1,
            due_date=due,
            is_paid=is_paid,
            paid_date=due if is_paid else None
        )
        
    # Completed Loan for Shravya to show History
    loan1_old = Loan.objects.create(
        member=m1,
        principal_amount=10000,
        interest_rate=10.0,
        duration_months=6,
        start_date=date(2024, 1, 15),
        status='completed'
    )
    emi_amount1_old = loan1_old.total_payable / loan1_old.duration_months
    for i in range(6):
        due = loan1_old.start_date + timedelta(days=30*(i+1))
        LoanEMI.objects.create(
            loan=loan1_old, amount=emi_amount1_old, due_date=due,
            is_paid=True, paid_date=due
        )

    # Active Loan for Latha (Member 2)
    m2 = g1_members[1]
    loan2 = Loan.objects.create(
        member=m2, principal_amount=50000, interest_rate=12.0,
        duration_months=24, start_date=date.today() - timedelta(days=150),
        status='active'
    )
    emi_amount2 = loan2.total_payable / loan2.duration_months
    for i in range(24):
        due = loan2.start_date + timedelta(days=30*(i+1))
        is_paid = i < 5
        LoanEMI.objects.create(
            loan=loan2, amount=emi_amount2, due_date=due,
            is_paid=is_paid, paid_date=due if is_paid else None
        )
        
    # Active Loan for Leader (Pavani)
    loan_leader = Loan.objects.create(
        member=l1, principal_amount=80000, interest_rate=12.0,
        duration_months=36, start_date=date(2025, 1, 15), status='active'
    )
    emi_leader = loan_leader.total_payable / loan_leader.duration_months
    for i in range(36):
        due = loan_leader.start_date + timedelta(days=30*(i+1))
        is_paid = i < 14
        LoanEMI.objects.create(
            loan=loan_leader, amount=emi_leader, due_date=due,
            is_paid=is_paid, paid_date=due if is_paid else None
        )
        
    print("Adding Savings...")
    for i in range(24):
        Savings.objects.create(
            member=m1, amount=500.00,
            month=date(2024 + (i//12), (i%12)+1, 1)
        )
            
    print("Adding Notifications...")
    Notification.objects.create(user=m1.user, title="Upcoming SHG Meeting", message="Meeting scheduled for 2026-03-12 at 08:30.", icon_type="calendar")
    Notification.objects.create(user=m1.user, title="Loan Repayment", message="₹2,000 paid for Loan ID: #1056.", icon_type="wallet")
    Notification.objects.create(user=m1.user, title="Contribution Due", message="Monthly Contribution: ₹500 due for Mar 2026.", icon_type="alert")
    
    print("Data seeded successfully!")
    print("\n--- Login Credentials ---")
    print("Admin (Kavitha): Mobile: 9951458910, OTP: 123")
    print("Leader (Pavani): Mobile: 9951458911, OTP: 123")
    print("Member (Shravya): Mobile: 9951458919, OTP: 123")
    print("Member (Lakshmi): Mobile: 9951458920, OTP: 123")

if __name__ == '__main__':
    seed()

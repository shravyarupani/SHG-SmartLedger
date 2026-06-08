from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('member', 'Member'),
        ('leader', 'Leader'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class SHGGroup(models.Model):
    name = models.CharField(max_length=255)
    village = models.CharField(max_length=255)
    formed_date = models.DateField(null=True, blank=True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_groups')
    
    def __str__(self):
        return self.name

class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shg_group = models.ForeignKey(SHGGroup, on_delete=models.CASCADE, related_name='members')
    is_leader = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    member_id = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    account_no = models.CharField(max_length=50, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Loan(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
    )
    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name='loans')
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2) # e.g., 2.00 for 2%
    duration_months = models.IntegerField()
    start_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    @property
    def total_interest(self):
        # Simple interest calculation assuming interest_rate is per annum and duration is in months
        return (self.principal_amount * self.interest_rate * self.duration_months) / 1200
        
    @property
    def total_payable(self):
        return self.principal_amount + self.total_interest
        
    def __str__(self):
        return f"{self.member} - {self.principal_amount} ({self.status})"

class LoanEMI(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='emis')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"EMI for {self.loan} - Due: {self.due_date}"

class Savings(models.Model):
    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name='savings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField() # Represents the month/year of the saving
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Savings for {self.member} - {self.month.strftime('%b %Y')}"

class MeetingAlert(models.Model):
    shg_group = models.ForeignKey(SHGGroup, on_delete=models.CASCADE, related_name='meetings')
    title = models.CharField(max_length=255)
    meeting_date = models.DateField()
    meeting_time = models.TimeField()
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.shg_group} on {self.meeting_date}"

class Notification(models.Model):
    ICON_CHOICES = (
        ('alert', 'Alert'),
        ('wallet', 'Wallet'),
        ('calendar', 'Calendar'),
        ('info', 'Info'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    icon_type = models.CharField(max_length=20, choices=ICON_CHOICES, default='info')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Notification for {self.user}: {self.title}"

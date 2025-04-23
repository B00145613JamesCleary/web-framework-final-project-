from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name

class PayHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='pay_histories')
    pay_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.employee.name} - {self.pay_date} - €{self.amount_paid}"


class TimeOffBalance(models.Model):
    employee = models.OneToOneField('Employee', on_delete=models.CASCADE, related_name='time_off_balance')
    holiday_days = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    sick_days = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    personal_days = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)

    def __str__(self):
        return f"{self.employee.name}'s Time-Off Balances"


class LeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=50, choices=[('Holiday', 'Holiday'), ('Sick', 'Sick'), ('Personal', 'Personal')])
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='Pending') 

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type} from {self.start_date} to {self.end_date} ({self.status})"


# Create your models here.

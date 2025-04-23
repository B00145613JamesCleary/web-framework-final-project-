from django.contrib import admin
from .models import Employee, PayHistory, TimeOffBalance, LeaveRequest

# Register all models only once
admin.site.register(Employee)
admin.site.register(PayHistory)
admin.site.register(TimeOffBalance)
admin.site.register(LeaveRequest)

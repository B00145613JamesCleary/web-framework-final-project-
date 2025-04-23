"""
URL configuration for webproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from payroll import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('pay_history/', views.pay_history, name='pay_history'),  
    path('log_pay/', views.log_pay, name='log_pay'),         
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/edit/<int:emp_id>/', views.edit_employee, name='edit_employee'),
    path('employees/delete/<int:emp_id>/', views.delete_employee, name='delete_employee'),
    path('download_payslip/', views.download_payslip, name='download_payslip'),
    path('time_off_balance/', views.time_off_balance, name='time_off_balance'),
    path('manage_time_off/', views.manage_time_off, name='manage_time_off'),
    path('edit_time_off/<int:emp_id>/', views.edit_time_off, name='edit_time_off'),
    path('add_time_off/', views.add_time_off, name='add_time_off'),
    path('delete_time_off/<int:emp_id>/', views.delete_time_off, name='delete_time_off'),
    path('request_leave/', views.request_leave, name='request_leave'),
    path('manage_leave_requests/', views.manage_leave_requests, name='manage_leave_requests'),
    path('update_leave_status/<int:leave_id>/', views.update_leave_status, name='update_leave_status'),






     
]

from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Employee, PayHistory, TimeOffBalance, LeaveRequest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO


def generate_navbar(request):
    if not request.user.is_authenticated:
        return ""

    if request.user.groups.filter(name="Managers").exists():
        navbar_html = """
            <div style="background-color:#007BFF;padding:10px;text-align:center;">
                <a href='/' style="color:white;margin-right:20px;">Home</a>
                <a href='/users/' style="color:white;margin-right:20px;">Manage Users</a>
                <a href='/employees/' style="color:white;margin-right:20px;">Manage Employees</a>
                <a href='/log_pay/' style="color:white;margin-right:20px;">Log Pay</a>
                <a href='/manage_time_off/' style="color:white;margin-right:20px;">Manage Time-Off</a>
                <a href='/manage_leave_requests/' style="color:white;margin-right:20px;">Manage Leave Requests</a>
                <a href='/logout/' style="color:white;">Logout</a>
            </div>
        """
    else:
        navbar_html = """
            <div style="background-color:#007BFF;padding:10px;text-align:center;">
                <a href='/' style="color:white;margin-right:20px;">Home</a>
                <a href='/pay_history/' style="color:white;margin-right:20px;">Pay History</a>
                <a href='/time_off_balance/' style="color:white;margin-right:20px;">Time Off</a>
                <a href='/request_leave/' style="color:white;margin-right:20px;">Request Leave</a>
                <a href='/logout/' style="color:white;">Logout</a>
            </div>
        """

    return navbar_html





@csrf_exempt
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    navbar = generate_navbar(request)
    username = request.user.username

    if request.user.groups.filter(name="Managers").exists():
        return HttpResponse(navbar + f"""
            <h1>Welcome Manager {username}!</h1>
        """)
    else:
        return HttpResponse(navbar + f"""
            <h1>Welcome, {username}, to the Leisure Payroll System!</h1>
        """)




@csrf_exempt
def employee_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name="Managers").exists():
        return HttpResponse("<h1>Access Denied</h1>")

    employees = Employee.objects.all()

    employee_html = "<h1>Employee List</h1><ul>"
    for emp in employees:
        employee_html += f"<li>{emp.name} - {emp.email} - <a href='/employees/edit/{emp.id}/'>Edit</a> | <a href='/employees/delete/{emp.id}/'>Delete</a></li>"
    employee_html += "</ul>"

    employee_html += """
        <a href="/employees/add/" style="display:inline-block;margin-top:20px;padding:10px;background-color:green;color:white;text-decoration:none;border-radius:5px;">Add New Employee</a><br><br>
        <a href="/" style="display:inline-block;margin-top:20px;">Back to Home</a>
    """

    return HttpResponse(employee_html)

def logout_view(request):
    logout(request)
    return redirect('login')


@csrf_exempt
def log_pay(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Only allow Managers
    if not request.user.groups.filter(name="Managers").exists():
        return HttpResponse("<h1>Access Denied</h1>")

    if request.method == 'POST':
        employee_name = request.POST.get('employee_name')
        pay_date = request.POST.get('pay_date')
        amount_paid = request.POST.get('amount_paid')
        notes = request.POST.get('notes')

        try:
            employee = Employee.objects.get(name=employee_name)
            PayHistory.objects.create(
                employee=employee,
                pay_date=pay_date,
                amount_paid=amount_paid,
                notes=notes
            )
            return HttpResponse("<h1>Pay entry added successfully!</h1><a href='/'>Back to Home</a>")
        except Employee.DoesNotExist:
            return HttpResponse("<h1>Employee not found.</h1><a href='/'>Back to Home</a>")

    return HttpResponse("""
        <h1>Log New Pay Entry</h1>
        <form method="post">
            <input type="text" name="employee_name" placeholder="Employee Name" required><br><br>
            <input type="date" name="pay_date" required><br><br>
            <input type="number" step="0.01" name="amount_paid" placeholder="Amount Paid" required><br><br>
            <textarea name="notes" placeholder="Notes (optional)"></textarea><br><br>
            <button type="submit" style="padding:10px; background-color:#28a745; color:white; border:none; border-radius:5px;">Submit Pay Entry</button>
        </form>
        <a href="/" style="display:inline-block;margin-top:20px;">Back to Home</a>
    """)



@csrf_exempt
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
    except User.DoesNotExist:
        return HttpResponse("User not found.")
    
    return redirect('user_list')



@csrf_exempt
def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        User.objects.create_user(username=username, email=email, password=password)
        return redirect('user_list')

    return HttpResponse("""
        <h1>Add New User</h1>
        <form method="post">
            <input type="text" name="username" placeholder="Username" required><br><br>
            <input type="email" name="email" placeholder="Email"><br><br>
            <input type="password" name="password" placeholder="Password" required><br><br>
            <button type="submit">Create User</button>
        </form>
        <a href="/users/" style="display:inline-block;margin-top:20px;">Back to User List</a>
    """)

@csrf_exempt
def edit_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse("User not found.")

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        return redirect('user_list')

    return HttpResponse(f"""
        <h1>Edit User: {user.username}</h1>
        <form method="post">
            <input type="text" name="username" value="{user.username}" required><br><br>
            <input type="email" name="email" value="{user.email}"><br><br>
            <button type="submit">Save Changes</button>
        </form>
        <a href="/users/" style="display:inline-block;margin-top:20px;">Back to User List</a>
    """)



@csrf_exempt
def user_list(request):
    users = User.objects.all()
    user_list_html = "<h1>User Management</h1><ul>"

    for user in users:
        user_list_html += f"<li>{user.username} - {user.email} - <a href='/users/edit/{user.id}/'>Edit</a> | <a href='/users/delete/{user.id}/'>Delete</a></li>"

    user_list_html += "</ul>"
    user_list_html += """
        <a href="/users/add/" style="display:inline-block;margin-top:20px;padding:10px;background-color:green;color:white;text-decoration:none;border-radius:5px;">Add New User</a>
    """
    return HttpResponse(user_list_html)

@csrf_exempt
def login_view(request):
    error_message = ""

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  
        else:
            error_message = "Invalid username or password."

    return HttpResponse(f"""
        <h1>Login to Leisure Payroll</h1>
        {'<p style="color:red;">' + error_message + '</p>' if error_message else ''}
        <form method="post">
            <input type="text" name="username" placeholder="Username" style="margin-bottom:10px;"><br>
            <input type="password" name="password" placeholder="Password" style="margin-bottom:10px;"><br>
            <button type="submit">Login</button>
        </form>
    """)

@csrf_exempt
def pay_history(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        employee = Employee.objects.get(name=request.user.username)
        pay_entries = PayHistory.objects.filter(employee=employee).order_by('-pay_date')
    except Employee.DoesNotExist:
        return HttpResponse("<h1>No Employee record found for this user.</h1><a href='/'>Back to Home</a>")

    total_salary = sum(entry.amount_paid for entry in pay_entries)

    pay_entries_html = f"""
        <h1>Pay History for {employee.name}</h1>
        <h2 style="color: green; text-align: center;">Total Salary Earned: €{total_salary:.2f}</h2>
        <table style="width: 80%; margin: 20px auto; border-collapse: collapse;">
            <thead>
                <tr style="background-color: #007BFF; color: white;">
                    <th style="padding: 10px; border: 1px solid #ddd;">Pay Date</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Amount Paid</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Notes</th>
                </tr>
            </thead>
            <tbody>
    """

    for entry in pay_entries:
        pay_entries_html += f"""
            <tr style="background-color: #f2f2f2;">
                <td style="padding: 10px; border: 1px solid #ddd;">{entry.pay_date}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">€{entry.amount_paid}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{entry.notes}</td>
            </tr>
        """

    pay_entries_html += f"""
            <tr style="background-color: #d4edda;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Total</td>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">€{total_salary:.2f}</td>
                <td style="padding: 10px; border: 1px solid #ddd;"></td>
            </tr>
            </tbody>
        </table>

        <div style="text-align: center; margin-top: 20px;">
            <a href="/download_payslip/" style="padding: 10px 20px; background-color: #17a2b8; color: white; text-decoration: none; border-radius: 5px;">Download Payslip (PDF)</a>
        </div>

        <div style="text-align: center; margin-top: 20px;">
            <a href="/" style="padding: 10px 20px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px;">Back to Home</a>
        </div>
    """

    return HttpResponse(generate_navbar(request) + pay_entries_html)



@csrf_exempt
def add_employee(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name="Managers").exists():
        return HttpResponse("<h1>Access Denied</h1>")

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        Employee.objects.create(name=name, email=email)
        return redirect('employee_list')

    return HttpResponse("""
        <h1>Add New Employee</h1>
        <form method="post">
            <input type="text" name="name" placeholder="Employee Name" required><br><br>
            <input type="email" name="email" placeholder="Employee Email" required><br><br>
            <button type="submit" style="padding:10px;background-color:green;color:white;">Add Employee</button>
        </form>
        <a href="/employees/" style="display:inline-block;margin-top:20px;">Back to Employee List</a>
    """)


@csrf_exempt
def edit_employee(request, emp_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name="Managers").exists():
        return HttpResponse("<h1>Access Denied</h1>")

    try:
        employee = Employee.objects.get(id=emp_id)
    except Employee.DoesNotExist:
        return HttpResponse("<h1>Employee not found.</h1>")

    if request.method == 'POST':
        employee.name = request.POST.get('name')
        employee.email = request.POST.get('email')
        employee.save()
        return redirect('employee_list')

    return HttpResponse(f"""
        <h1>Edit Employee: {employee.name}</h1>
        <form method="post">
            <input type="text" name="name" value="{employee.name}" required><br><br>
            <input type="email" name="email" value="{employee.email}" required><br><br>
            <button type="submit" style="padding:10px;background-color:orange;color:white;">Save Changes</button>
        </form>
        <a href="/employees/" style="display:inline-block;margin-top:20px;">Back to Employee List</a>
    """)


@csrf_exempt
def delete_employee(request, emp_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name="Managers").exists():
        return HttpResponse("<h1>Access Denied</h1>")

    try:
        employee = Employee.objects.get(id=emp_id)
        employee.delete()
        return redirect('employee_list')
    except Employee.DoesNotExist:
        return HttpResponse("<h1>Employee not found.</h1>")

@csrf_exempt
def download_payslip(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        employee = Employee.objects.get(name=request.user.username)
        pay_entries = PayHistory.objects.filter(employee=employee).order_by('-pay_date')
    except Employee.DoesNotExist:
        return HttpResponse("<h1>No Employee record found for this user.</h1>")

    # Prepare context data
    context = {
        'employee': employee,
        'pay_entries': pay_entries,
    }

    # Render HTML
    html = render_to_string('payslip_template.html', context)

    # Generate PDF
    response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), response)

    if not pdf.err:
        return HttpResponse(response.getvalue(), content_type='application/pdf')

    return HttpResponse('We had some errors generating the payslip.')


@csrf_exempt
def download_payslip(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        employee = Employee.objects.get(name=request.user.username)
        pay_entries = PayHistory.objects.filter(employee=employee).order_by('-pay_date')
    except Employee.DoesNotExist:
        return HttpResponse("<h1>No Employee record found for this user.</h1>")

    # Create PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 18)
    p.drawString(200, height - 50, "Payslip")

    # Employee Info
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Employee: {employee.name}")
    p.drawString(50, height - 120, f"Email: {employee.email}")

    # Table Headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 160, "Pay Date")
    p.drawString(200, height - 160, "Amount Paid (€)")
    p.drawString(400, height - 160, "Notes")

    # Table Content
    y = height - 180
    p.setFont("Helvetica", 10)
    for entry in pay_entries:
        p.drawString(50, y, str(entry.pay_date))
        p.drawString(200, y, f"€{entry.amount_paid}")
        p.drawString(400, y, entry.notes if entry.notes else "-")
        y -= 20
        if y < 50:  # Create a new page if out of space
            p.showPage()
            y = height - 50

    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type='application/pdf')


@csrf_exempt
def time_off_balance(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        employee = Employee.objects.get(name=request.user.username)
        balance = employee.time_off_balance
    except (Employee.DoesNotExist, TimeOffBalance.DoesNotExist):
        return HttpResponse("<h1>No time-off record available.</h1><a href='/'>Back to Home</a>")

    page_html = f"""
        <h1>Time-Off Balance for {employee.name}</h1>
        <ul style="list-style:none;">
            <li>Holiday Days Left: {balance.holiday_days}</li>
            <li>Sick Days Left: {balance.sick_days}</li>
            <li>Personal Days Left: {balance.personal_days}</li>
        </ul>
    """

    return HttpResponse(generate_navbar(request) + page_html)


@csrf_exempt
def manage_time_off(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name="Managers").exists():
        return HttpResponse("<h1>Access Denied</h1>")

    employees = Employee.objects.all()

    page_html = "<h1>Manage Employee Time-Off Balances</h1><ul>"

    for emp in employees:
        try:
            balance = emp.time_off_balance
            page_html += f"""
                <li>
                    <strong>{emp.name}</strong> - 
                    Holiday: {balance.holiday_days}, 
                    Sick: {balance.sick_days}, 
                    Personal: {balance.personal_days}
                    <a href="/edit_time_off/{emp.id}/" style="margin-left:20px;">Edit</a>
                </li>
            """
        except TimeOffBalance.DoesNotExist:
            page_html += f"<li>{emp.name} - No balance found</li>"

    page_html += "</ul><a href='/' style='display:inline-block;margin-top:20px;'>Back to Home</a>"

    return HttpResponse(generate_navbar(request) + page_html)


@csrf_exempt
def edit_time_off(request, emp_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name="Managers").exists():
        return HttpResponse("<h1>Access Denied</h1>")

    try:
        employee = Employee.objects.get(id=emp_id)
        balance = employee.time_off_balance
    except (Employee.DoesNotExist, TimeOffBalance.DoesNotExist):
        return HttpResponse("<h1>Employee or balance not found.</h1>")

    if request.method == 'POST':
        balance.holiday_days = request.POST.get('holiday_days')
        balance.sick_days = request.POST.get('sick_days')
        balance.personal_days = request.POST.get('personal_days')
        balance.save()
        return redirect('manage_time_off')

    return HttpResponse(generate_navbar(request) + f"""
        <h1>Edit Time-Off for {employee.name}</h1>
        <form method="post">
            <label>Holiday Days:</label><br>
            <input type="number" step="0.01" name="holiday_days" value="{balance.holiday_days}" required><br><br>
            <label>Sick Days:</label><br>
            <input type="number" step="0.01" name="sick_days" value="{balance.sick_days}" required><br><br>
            <label>Personal Days:</label><br>
            <input type="number" step="0.01" name="personal_days" value="{balance.personal_days}" required><br><br>
            <button type="submit" style="padding:10px;background-color:#28a745;color:white;border:none;border-radius:5px;">Save Changes</button>
        </form>
        <br>
        <a href="/manage_time_off/" style="margin-top:20px;">Back to Manage Time-Off</a>
    """)

@csrf_exempt
def add_time_off(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name="Managers").exists():
        return HttpResponse("<h1>Access Denied</h1>")

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        holiday_days = request.POST.get('holiday_days')
        sick_days = request.POST.get('sick_days')
        personal_days = request.POST.get('personal_days')

        try:
            employee = Employee.objects.get(id=employee_id)
            # Only create if not already existing
            if not hasattr(employee, 'time_off_balance'):
                TimeOffBalance.objects.create(
                    employee=employee,
                    holiday_days=holiday_days,
                    sick_days=sick_days,
                    personal_days=personal_days
                )
        except Employee.DoesNotExist:
            return HttpResponse("<h1>Employee not found.</h1>")

        return redirect('manage_time_off')

    employees = Employee.objects.all()

    employee_options = ""
    for emp in employees:
        if not hasattr(emp, 'time_off_balance'):  # only show if no balance exists yet
            employee_options += f"<option value='{emp.id}'>{emp.name}</option>"

    if employee_options == "":
        employee_options = "<option disabled>No eligible employees</option>"

    return HttpResponse(generate_navbar(request) + f"""
        <h1>Add New Time-Off Balance</h1>
        <form method="post">
            <label>Employee:</label><br>
            <select name="employee_id" required>
                {employee_options}
            </select><br><br>

            <label>Holiday Days:</label><br>
            <input type="number" step="0.01" name="holiday_days" required><br><br>
            <label>Sick Days:</label><br>
            <input type="number" step="0.01" name="sick_days" required><br><br>
            <label>Personal Days:</label><br>
            <input type="number" step="0.01" name="personal_days" required><br><br>

            <button type="submit" style="padding:10px;background-color:green;color:white;border:none;border-radius:5px;">Add Balance</button>
        </form>
        <a href="/manage_time_off/" style="display:inline-block;margin-top:20px;">Back to Manage Time-Off</a>
    """)

@csrf_exempt
def delete_time_off(request, emp_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name="Managers").exists():
        return HttpResponse("<h1>Access Denied</h1>")

    try:
        employee = Employee.objects.get(id=emp_id)
        employee.time_off_balance.delete()
    except (Employee.DoesNotExist, TimeOffBalance.DoesNotExist):
        return HttpResponse("<h1>Employee or balance not found.</h1>")

    return redirect('manage_time_off')


@csrf_exempt
def request_leave(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        employee = Employee.objects.get(name=request.user.username)
    except Employee.DoesNotExist:
        return HttpResponse("<h1>Employee not found.</h1>")

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        leave_type = request.POST.get('leave_type')
        reason = request.POST.get('reason')

        LeaveRequest.objects.create(
            employee=employee,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            reason=reason
        )
        return HttpResponse("<h1>Leave request submitted successfully!</h1><a href='/'>Back to Home</a>")

    return HttpResponse(generate_navbar(request) + """
        <h1>Request Leave</h1>
        <form method="post">
            <label>Start Date:</label><br>
            <input type="date" name="start_date" required><br><br>
            <label>End Date:</label><br>
            <input type="date" name="end_date" required><br><br>
            <label>Leave Type:</label><br>
            <select name="leave_type" required>
                <option value="Holiday">Holiday</option>
                <option value="Sick">Sick</option>
                <option value="Personal">Personal</option>
            </select><br><br>
            <label>Reason:</label><br>
            <textarea name="reason" placeholder="Reason (optional)"></textarea><br><br>
            <button type="submit" style="padding:10px;background-color:green;color:white;">Submit Request</button>
        </form>
    """)


@csrf_exempt
def manage_leave_requests(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name="Managers").exists():
        return HttpResponse("<h1>Access Denied</h1>")

    leave_requests = LeaveRequest.objects.all().order_by('-start_date')

    page_html = "<h1>Manage Leave Requests</h1><ul>"

    for leave in leave_requests:
        page_html += f"""
            <li>
                <strong>{leave.employee.name}</strong> - {leave.leave_type} from {leave.start_date} to {leave.end_date}
                - Status: <strong>{leave.status}</strong>
                <br>Reason: {leave.reason}
                <br>
        """
        if leave.status == 'Pending':
            page_html += f"""
                <form method="post" action="/update_leave_status/{leave.id}/" style="margin-top:10px;">
                    <input type="hidden" name="action" value="Approve">
                    <button type="submit" style="background-color:green;color:white;padding:5px 10px;margin-right:10px;">Approve</button>
                </form>

                <form method="post" action="/update_leave_status/{leave.id}/" style="display:inline;">
                    <input type="hidden" name="action" value="Deny">
                    <button type="submit" style="background-color:red;color:white;padding:5px 10px;">Deny</button>
                </form>
            """
        page_html += "</li><hr>"

    page_html += "</ul><a href='/' style='display:inline-block;margin-top:20px;'>Back to Home</a>"

    return HttpResponse(generate_navbar(request) + page_html)


@csrf_exempt
def update_leave_status(request, leave_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name="Managers").exists():
        return HttpResponse("<h1>Access Denied</h1>")

    try:
        leave = LeaveRequest.objects.get(id=leave_id)
    except LeaveRequest.DoesNotExist:
        return HttpResponse("<h1>Leave request not found.</h1>")

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == "Approve":
            leave.status = 'Approved'
            leave.save()
        elif action == "Deny":
            leave.status = 'Denied'
            leave.save()

    return redirect('manage_leave_requests')


from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from functools import wraps
from decimal import Decimal, InvalidOperation
import re
from datetime import date
from sqlalchemy import func, or_

from app import db
from app.models import User, Employee, Attendance, LeaveRequest, Payroll
from app.validation import clean_text, validate_email, validate_password, validate_phone, validate_salary, validate_iso_date


# =====================================
# AUTHENTICATION BLUEPRINT
# =====================================

auth = Blueprint("auth", __name__)


# =====================================
# USER REGISTRATION
# =====================================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        try:
            username = clean_text(request.form.get("username"), "Username", required=True, max_length=100)
            if len(username) < 2:
                raise ValueError("Username must contain at least 2 characters.")
            email = validate_email(request.form.get("email"))
            password = validate_password(request.form.get("password"))
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(
            username=username,
            email=email,
            role="employee"
        )

        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# =====================================
# USER LOGIN
# =====================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or len(email) > 150 or not password or len(password) > 128:
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            login_user(user)

            flash("Login successful.", "success")

            return redirect(url_for("auth.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


# =====================================
# DASHBOARD
# =====================================

@auth.route("/dashboard")
@login_required
def dashboard():

    # Employees receive a private dashboard containing only their own records.
    if current_user.role != "admin":
        employee = Employee.query.filter_by(user_id=current_user.id).first()
        if not employee:
            return render_template("employee_dashboard.html", user=current_user,
                                   employee=None, attendance_records=[],
                                   leave_requests=[], payroll_records=[])

        attendance_records = Attendance.query.filter_by(
            employee_id=employee.id
        ).order_by(Attendance.attendance_date.desc()).limit(10).all()
        leave_requests = LeaveRequest.query.filter_by(
            employee_id=employee.id
        ).order_by(LeaveRequest.created_at.desc()).limit(10).all()
        payroll_records = Payroll.query.filter_by(
            employee_id=employee.id
        ).order_by(Payroll.pay_month.desc()).limit(6).all()

        return render_template(
            "employee_dashboard.html",
            user=current_user,
            employee=employee,
            attendance_records=attendance_records,
            leave_requests=leave_requests,
            payroll_records=payroll_records
        )

    total_employees = Employee.query.count()

    total_departments = db.session.query(
        func.count(func.distinct(Employee.department))
    ).filter(
        Employee.department.isnot(None),
        Employee.department != ""
    ).scalar() or 0

    average_salary = db.session.query(
        func.avg(Employee.salary)
    ).scalar() or 0

    total_payroll = db.session.query(
        func.sum(Employee.salary)
    ).scalar() or 0

    department_data = db.session.query(
        Employee.department,
        func.count(Employee.id)
    ).filter(
        Employee.department.isnot(None),
        Employee.department != ""
    ).group_by(
        Employee.department
    ).all()

    recent_employees = Employee.query.order_by(
        Employee.id.desc()
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        user=current_user,
        total_employees=total_employees,
        total_departments=total_departments,
        average_salary=average_salary,
        total_payroll=total_payroll,
        department_data=department_data,
        recent_employees=recent_employees
    )


# =====================================
# USER LOGOUT
# =====================================

@auth.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    flash("You have been logged out.", "success")

    return redirect(url_for("auth.login"))


# =====================================
# EMPLOYEE MANAGEMENT BLUEPRINT
# =====================================

employee_bp = Blueprint(
    "employees",
    __name__,
    url_prefix="/employees"
)


# =====================================
# ADMIN AUTHORIZATION
# =====================================

def admin_required(func):

    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):

        if current_user.role != "admin":
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("auth.dashboard"))

        return func(*args, **kwargs)

    return wrapper


# =====================================
# EMPLOYEE PROFILE
# =====================================

@employee_bp.route("/<int:id>")
@admin_required
def employee_profile(id):

    employee = db.get_or_404(Employee, id)

    return render_template(
        "employee_profile.html",
        employee=employee
    )


# =====================================
# VIEW, SEARCH AND FILTER EMPLOYEES
# =====================================

@employee_bp.route("/")
@admin_required
def list_employees():

    search = request.args.get("search", "").strip()
    department = request.args.get("department", "").strip()

    query = Employee.query

    if search:

        search_term = f"%{search}%"

        query = query.filter(
            or_(
                Employee.first_name.ilike(search_term),
                Employee.last_name.ilike(search_term),
                Employee.email.ilike(search_term),
                func.concat(
                    Employee.first_name,
                    " ",
                    Employee.last_name
                ).ilike(search_term)
            )
        )

    if department:

        query = query.filter(
            Employee.department == department
        )

    employees = query.order_by(
        Employee.id.desc()
    ).all()

    departments = db.session.query(
        Employee.department
    ).filter(
        Employee.department.isnot(None),
        Employee.department != ""
    ).distinct().order_by(
        Employee.department
    ).all()

    department_list = [
        row[0] for row in departments
    ]

    total_results = len(employees)

    return render_template(
        "employees.html",
        employees=employees,
        departments=department_list,
        search=search,
        selected_department=department,
        total_results=total_results
    )


# =====================================
# ADD EMPLOYEE
# =====================================

@employee_bp.route("/add", methods=["GET", "POST"])
@admin_required
def add_employee():

    if request.method == "POST":

        try:
            first_name = clean_text(request.form.get("first_name"), "First name", required=True, max_length=100)
            last_name = clean_text(request.form.get("last_name"), "Last name", required=True, max_length=100)
            email = validate_email(request.form.get("email"))
            phone = validate_phone(request.form.get("phone"))
            department = clean_text(request.form.get("department"), "Department", max_length=100)
            designation = clean_text(request.form.get("designation"), "Designation", max_length=100)
            salary = validate_salary(request.form.get("salary"))
            joining_date = validate_iso_date(request.form.get("joining_date"), "joining date", default_today=True)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("employees.add_employee"))

        existing_employee = Employee.query.filter_by(
            email=email
        ).first()

        if existing_employee:
            flash("An employee with this email already exists.", "danger")
            return redirect(url_for("employees.add_employee"))

        new_employee = Employee(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            department=department,
            designation=designation,
            salary=salary,
            joining_date=joining_date
        )

        try:
            db.session.add(new_employee)
            db.session.commit()

            flash("Employee added successfully!", "success")

            return redirect(url_for("employees.list_employees"))

        except Exception:
            db.session.rollback()
            flash("Unable to add employee.", "danger")

    return render_template("employee_form.html", employee=None)


# =====================================
# UPDATE EMPLOYEE
# =====================================

@employee_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_employee(id):

    employee = db.get_or_404(Employee, id)

    if request.method == "POST":

        try:
            employee.first_name = clean_text(request.form.get("first_name"), "First name", required=True, max_length=100)
            employee.last_name = clean_text(request.form.get("last_name"), "Last name", required=True, max_length=100)
            employee.email = validate_email(request.form.get("email"))
            employee.phone = validate_phone(request.form.get("phone"))
            employee.department = clean_text(request.form.get("department"), "Department", max_length=100)
            employee.designation = clean_text(request.form.get("designation"), "Designation", max_length=100)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("employees.edit_employee", id=id))

        email_exists = Employee.query.filter(
            Employee.email == employee.email,
            Employee.id != employee.id
        ).first()

        if email_exists:
            flash("Another employee already uses this email.", "danger")
            return redirect(url_for("employees.edit_employee", id=id))

        try:
            employee.salary = validate_salary(request.form.get("salary"))
            employee.joining_date = validate_iso_date(request.form.get("joining_date"), "joining date", default_today=True)

            db.session.commit()

            flash("Employee updated successfully!", "success")

            return redirect(url_for("employees.list_employees"))

        except (InvalidOperation, ValueError):
            db.session.rollback()
            flash("Please check the employee details and try again.", "danger")

        except Exception:
            db.session.rollback()
            flash("Unable to update employee.", "danger")

        employee = db.get_or_404(Employee, id)

    return render_template(
        "employee_form.html",
        employee=employee
    )


# =====================================
# DELETE EMPLOYEE
# =====================================

@employee_bp.route("/delete/<int:id>", methods=["POST"])
@admin_required
def delete_employee(id):

    employee = db.get_or_404(Employee, id)

    try:
        db.session.delete(employee)
        db.session.commit()

        flash("Employee deleted successfully!", "success")

    except Exception:
        db.session.rollback()
        flash("Unable to delete employee.", "danger")

    return redirect(url_for("employees.list_employees"))

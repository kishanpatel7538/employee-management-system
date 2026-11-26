
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
import csv
import io

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, Response
)
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from app.models import Employee, Attendance, LeaveRequest, Payroll, User
from app.routes import admin_required
from app.validation import clean_text, validate_salary, validate_iso_date


hr_bp = Blueprint("hr", __name__, url_prefix="/hr")


def _employee_for_current_user():
    return Employee.query.filter_by(user_id=current_user.id).first()


# =====================================
# ATTENDANCE
# =====================================

@hr_bp.route("/attendance", methods=["GET", "POST"])
@login_required
def attendance():

    if current_user.role != "admin":
        employee = _employee_for_current_user()

        if not employee:
            flash(
                "Your login is not linked to an employee profile. Contact an administrator.",
                "warning"
            )
            return redirect(url_for("auth.dashboard"))
    else:
        employee = None

    selected_date = request.args.get("date", date.today().isoformat())

    try:
        work_date = date.fromisoformat(selected_date)
    except ValueError:
        work_date = date.today()

    if request.method == "POST":

        if current_user.role != "admin":
            flash("Only administrators can record attendance.", "danger")
            return redirect(url_for("hr.attendance"))

        try:
            employee_id = int(request.form.get("employee_id", ""))
            status = request.form.get("status", "present")

            if status not in {"present", "absent", "half_day", "leave"}:
                raise ValueError()

            record_date = validate_iso_date(
                request.form.get("attendance_date"),
                "attendance date"
            )

            if record_date > date.today():
                raise ValueError("Attendance date cannot be in the future.")

            if not db.session.get(Employee, employee_id):
                raise ValueError("Select an existing employee.")

            check_in = (
                time.fromisoformat(request.form["check_in"])
                if request.form.get("check_in") else None
            )

            check_out = (
                time.fromisoformat(request.form["check_out"])
                if request.form.get("check_out") else None
            )

            if status == "absent" and (check_in or check_out):
                raise ValueError(
                    "Absent attendance cannot have check-in or check-out times."
                )

            if check_in and check_out and check_out <= check_in:
                raise ValueError("Check-out must be later than check-in.")

            record = Attendance.query.filter_by(
                employee_id=employee_id,
                attendance_date=record_date
            ).first()

            if not record:
                record = Attendance(
                    employee_id=employee_id,
                    attendance_date=record_date
                )
                db.session.add(record)

            record.status = status
            record.check_in = check_in
            record.check_out = check_out
            record.notes = clean_text(
                request.form.get("notes"),
                "Notes",
                max_length=500
            )

            db.session.commit()
            flash("Attendance saved.", "success")

        except (ValueError, TypeError):
            db.session.rollback()
            flash("Please provide valid attendance details.", "danger")

        return redirect(
            url_for(
                "hr.attendance",
                date=request.form.get(
                    "attendance_date",
                    date.today().isoformat()
                )
            )
        )

    query = Attendance.query.filter_by(attendance_date=work_date)

    if employee:
        query = query.filter_by(employee_id=employee.id)

    records = query.order_by(Attendance.id.desc()).all()

    employees = (
        Employee.query.order_by(Employee.first_name).all()
        if current_user.role == "admin" else []
    )

    return render_template(
        "hr/attendance.html",
        records=records,
        employees=employees,
        work_date=work_date,
        is_admin=current_user.role == "admin"
    )


# =====================================
# LEAVES
# =====================================

@hr_bp.route("/leaves", methods=["GET", "POST"])
@login_required
def leaves():

    employee = _employee_for_current_user()

    if request.method == "POST":

        if not employee:
            flash(
                "Your account is not linked to an employee profile.",
                "warning"
            )
            return redirect(url_for("hr.leaves"))

        try:
            start = validate_iso_date(
                request.form.get("start_date"),
                "start date"
            )

            end = validate_iso_date(
                request.form.get("end_date"),
                "end date"
            )

            leave_type = (
                request.form.get("leave_type") or ""
            ).strip().lower()

            reason = clean_text(
                request.form.get("reason"),
                "Reason",
                required=True,
                max_length=2000
            )

            if end < start:
                raise ValueError(
                    "Leave end date cannot be before the start date."
                )

            if (end - start).days > 90:
                raise ValueError(
                    "A single leave request cannot exceed 91 calendar days."
                )

            if start < date.today():
                raise ValueError("Leave requests cannot start in the past.")

            if leave_type not in {"casual", "sick", "annual", "unpaid"}:
                raise ValueError("Select a valid leave type.")

            overlap = LeaveRequest.query.filter(
                LeaveRequest.employee_id == employee.id,
                func.lower(LeaveRequest.status).in_(["pending", "approved"]),
                LeaveRequest.start_date <= end,
                LeaveRequest.end_date >= start
            ).first()

            if overlap:
                raise ValueError(
                    "This request overlaps an existing pending or approved leave."
                )

            db.session.add(
                LeaveRequest(
                    employee_id=employee.id,
                    leave_type=leave_type,
                    start_date=start,
                    end_date=end,
                    reason=reason
                )
            )

            db.session.commit()
            flash("Leave request submitted.", "success")

        except ValueError as exc:
            db.session.rollback()
            flash(
                str(exc) or "Check the leave dates, type and reason.",
                "danger"
            )

        return redirect(url_for("hr.leaves"))

    query = LeaveRequest.query

    if current_user.role != "admin":
        query = (
            query.filter_by(employee_id=employee.id)
            if employee else query.filter_by(id=-1)
        )

    requests = query.order_by(
        LeaveRequest.created_at.desc()
    ).all()

    employees = (
        Employee.query.order_by(Employee.first_name).all()
        if current_user.role == "admin" else []
    )

    return render_template(
        "hr/leaves.html",
        requests=requests,
        employee=employee,
        employees=employees,
        is_admin=current_user.role == "admin"
    )


# =====================================
# LEAVE DECISION
# =====================================

@hr_bp.route("/leaves/<int:request_id>/decision", methods=["POST"])
@admin_required
def leave_decision(request_id):

    leave = db.get_or_404(LeaveRequest, request_id)
    decision = request.form.get("decision")

    if decision not in {"approved", "rejected"}:
        flash("Invalid leave decision.", "danger")

    else:
        try:
            leave.admin_comment = clean_text(
                request.form.get("admin_comment"),
                "Admin comment",
                max_length=500
            )

            leave.status = decision
            db.session.commit()

        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
            return redirect(url_for("hr.leaves"))

        flash(f"Leave request {decision}.", "success")

    return redirect(url_for("hr.leaves"))


# =====================================
# PAYROLL
# =====================================

@hr_bp.route("/payroll", methods=["GET", "POST"])
@admin_required
def payroll():

    if request.method == "POST":

        month = request.form.get("pay_month", "")

        try:
            datetime.strptime(month, "%Y-%m")

            if month < "2000-01" or month > "2100-12":
                raise ValueError(
                    "Enter a payroll month between 2000-01 and 2100-12."
                )

            allowances = validate_salary(
                request.form.get("allowances", "0") or "0",
                required=True
            )

            deductions = validate_salary(
                request.form.get("deductions", "0") or "0",
                required=True
            )

            employees = Employee.query.filter(
                Employee.salary.isnot(None)
            ).all()

            for emp in employees:

                basic = Decimal(emp.salary)

                if deductions > basic + allowances:
                    raise ValueError(
                        "Deductions cannot exceed basic salary plus allowances."
                    )

                existing = Payroll.query.filter_by(
                    employee_id=emp.id,
                    pay_month=month
                ).first()

                if existing:
                    continue

                db.session.add(
                    Payroll(
                        employee_id=emp.id,
                        pay_month=month,
                        basic_salary=basic,
                        allowances=allowances,
                        deductions=deductions,
                        net_salary=basic + allowances - deductions
                    )
                )

            db.session.commit()

            flash(
                "Payroll generated. Existing employee/month entries were skipped.",
                "success"
            )

        except (ValueError, InvalidOperation) as exc:
            db.session.rollback()
            flash(
                str(exc) or "Enter a valid month and non-negative payroll amounts.",
                "danger"
            )

        return redirect(url_for("hr.payroll"))

    records = Payroll.query.order_by(
        Payroll.pay_month.desc(),
        Payroll.id.desc()
    ).all()

    return render_template("hr/payroll.html", records=records)


# =====================================
# EMPLOYEE ACCOUNT LINKING
# =====================================

@hr_bp.route("/account-linking", methods=["GET", "POST"])
@admin_required
def account_linking():

    # LINK ACCOUNT
    if request.method == "POST":

        try:
            employee_id = int(
                request.form.get("employee_id", "")
            )

            user_id = int(
                request.form.get("user_id", "")
            )

            employee = db.session.get(Employee, employee_id)
            user = db.session.get(User, user_id)

            if employee is None:
                raise ValueError("Please select a valid employee.")

            if user is None:
                raise ValueError("Please select a valid login account.")

            if employee.user_id is not None:
                raise ValueError(
                    "This employee already has a linked login account."
                )

            if (user.role or "").strip().lower() != "employee":
                raise ValueError(
                    "Only employee-role accounts can be linked."
                )

            if user.employee is not None:
                raise ValueError(
                    "This login account is already linked to another employee."
                )

            # Save relationship in PostgreSQL.
            employee.user_id = user.id

            db.session.commit()

            flash(
                f"Login account {user.email} successfully linked to "
                f"{employee.first_name} {employee.last_name}.",
                "success"
            )

        except (ValueError, TypeError) as exc:
            db.session.rollback()
            flash(
                str(exc) or "Select a valid employee and login account.",
                "danger"
            )

        except Exception:
            db.session.rollback()
            flash(
                "Unable to link the account. Please check the server log and try again.",
                "danger"
            )

        return redirect(url_for("hr.account_linking"))

    # EMPLOYEES WITHOUT LOGIN ACCOUNTS
    unlinked_employees = (
        Employee.query
        .filter(Employee.user_id.is_(None))
        .order_by(Employee.first_name, Employee.last_name)
        .all()
    )

    # AVAILABLE EMPLOYEE LOGIN ACCOUNTS
    unlinked_users = (
        User.query
        .filter(
            func.lower(func.trim(User.role)) == "employee",
            ~User.employee.has()
        )
        .order_by(User.username)
        .all()
    )

    # ALREADY LINKED EMPLOYEES
    linked_employees = (
        Employee.query
        .filter(Employee.user_id.isnot(None))
        .order_by(Employee.first_name, Employee.last_name)
        .all()
    )

    return render_template(
        "hr/account_linking.html",
        unlinked_employees=unlinked_employees,
        unlinked_users=unlinked_users,
        linked_employees=linked_employees
    )


# =====================================
# EMPLOYEE PROFILE
# =====================================

@hr_bp.route("/my-profile")
@login_required
def my_profile():

    if current_user.role == "admin":
        flash(
            "Administrators should use the employee directory.",
            "info"
        )
        return redirect(url_for("employees.list_employees"))

    employee = _employee_for_current_user()

    if not employee:
        flash(
            "No employee record is linked to your login. Contact HR to link your account.",
            "warning"
        )
        return redirect(url_for("auth.dashboard"))

    return render_template(
        "employee_my_profile.html",
        employee=employee
    )


# =====================================
# MY PAYROLL
# =====================================

@hr_bp.route("/my-payroll")
@login_required
def my_payroll():

    if current_user.role == "admin":
        return redirect(url_for("hr.payroll"))

    employee = _employee_for_current_user()

    if not employee:
        flash(
            "No employee record is linked to your login. Contact HR.",
            "warning"
        )
        return redirect(url_for("auth.dashboard"))

    records = Payroll.query.filter_by(
        employee_id=employee.id
    ).order_by(
        Payroll.pay_month.desc()
    ).all()

    return render_template(
        "hr/my_payroll.html",
        employee=employee,
        records=records
    )


# =====================================
# EMPLOYEE CSV REPORT
# =====================================

@hr_bp.route("/reports/employees.csv")
@admin_required
def employee_report():

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "First name", "Last name", "Email",
        "Phone", "Department", "Designation",
        "Salary", "Joining date"
    ])

    for e in Employee.query.order_by(Employee.id).all():
        writer.writerow([
            e.id, e.first_name, e.last_name, e.email,
            e.phone, e.department, e.designation,
            e.salary, e.joining_date
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=employees.csv"
        }
    )


# =====================================
# ATTENDANCE CSV REPORT
# =====================================

@hr_bp.route("/reports/attendance.csv")
@admin_required
def attendance_report():

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Employee ID", "Employee", "Date",
        "Status", "Check in", "Check out", "Notes"
    ])

    for a in Attendance.query.order_by(
        Attendance.attendance_date.desc()
    ).all():

        writer.writerow([
            a.employee_id,
            f"{a.employee.first_name} {a.employee.last_name}",
            a.attendance_date,
            a.status,
            a.check_in,
            a.check_out,
            a.notes
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=attendance.csv"
        }
    )


# =====================================
# PAYROLL CSV REPORT
# =====================================

@hr_bp.route("/reports/payroll.csv")
@admin_required
def payroll_report():

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Employee ID", "Employee", "Month",
        "Basic", "Allowances", "Deductions", "Net salary"
    ])

    for p in Payroll.query.order_by(
        Payroll.pay_month.desc()
    ).all():

        writer.writerow([
            p.employee_id,
            f"{p.employee.first_name} {p.employee.last_name}",
            p.pay_month,
            p.basic_salary,
            p.allowances,
            p.deductions,
            p.net_salary
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=payroll.csv"
        }
    )

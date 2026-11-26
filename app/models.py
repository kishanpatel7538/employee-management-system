from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="employee", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship("Employee", back_populates="user", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Employee(db.Model):
    __tablename__ = "employees"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    salary = db.Column(db.Numeric(12, 2))
    joining_date = db.Column(db.Date, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=True)
    user = db.relationship("User", back_populates="employee")


class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    attendance_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    status = db.Column(db.String(20), nullable=False, default="present")
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    notes = db.Column(db.String(500))
    employee = db.relationship("Employee", backref=db.backref("attendance_records", lazy=True))
    __table_args__ = (db.UniqueConstraint("employee_id", "attendance_date", name="uq_attendance_employee_date"),)


class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    leave_type = db.Column(db.String(40), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    admin_comment = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship("Employee", backref=db.backref("leave_requests", lazy=True))


class Payroll(db.Model):
    __tablename__ = "payroll"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    pay_month = db.Column(db.String(7), nullable=False)  # YYYY-MM
    basic_salary = db.Column(db.Numeric(12, 2), nullable=False)
    allowances = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    deductions = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    net_salary = db.Column(db.Numeric(12, 2), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship("Employee", backref=db.backref("payroll_records", lazy=True))
    __table_args__ = (db.UniqueConstraint("employee_id", "pay_month", name="uq_payroll_employee_month"),)

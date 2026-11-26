# Employee Management System / HRMS

## Features
- Existing user registration/login, admin authorization, employee CRUD, employee search/filter and dashboard.
- Employee profile pages.
- Attendance recording and date-based viewing.
- Leave requests and administrator approval/rejection.
- Monthly payroll generation and payroll history.
- CSV exports for employees, attendance and payroll.

## Windows setup
1. Extract this project.
2. Open the `employee_management` folder in VS Code.
3. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` and enter your own PostgreSQL password and database name.
6. Ensure the PostgreSQL database exists (for example `employee_db`).
7. Start:
   ```powershell
   python run.py
   ```

## Database migration warning
`db.create_all()` creates missing tables but does not add new tables/columns to existing tables in all migration scenarios. The new modules introduce `attendance`, `leave_requests`, and `payroll` tables. Restart the app once to create these new tables. If you later change existing model columns, use Flask-Migrate/Alembic rather than relying on `create_all()`.

## Important account setup
New registrations receive the `employee` role. To grant administrator access, update the intended account in PostgreSQL:
```sql
UPDATE users SET role = 'admin' WHERE email = 'your-admin-email@example.com';
```
Employee self-service attendance/leave pages require a linked employee profile (`employees.user_id` must reference that user's `users.id`). Link an account only after confirming the correct user and employee:
```sql
UPDATE employees SET user_id = 1 WHERE id = 1;
```
Do not assign the same user to multiple employees.

## Payroll note
The current payroll generator applies the same entered allowance and deduction amounts to each employee, using each employee's stored salary as basic salary. This is a starter payroll workflow, not a statutory payroll/tax calculator. Validate local tax, PF, ESI and other legal rules before using it for real payroll.

## Security / production
This is a development portfolio application. Before production deployment, add CSRF protection (Flask-WTF), stronger role/permission policies, HTTPS, secure cookie settings, rate limiting, database backups, audit logging, and managed migrations. Do not commit `.env` or credentials.


## Employee portal updates
- Employee accounts see a separate private dashboard at `/dashboard`.
- Employees can view their own profile at `/hr/my-profile`, attendance at `/hr/attendance`, leave requests at `/hr/leaves`, and payroll at `/hr/my-payroll`.
- Employee accounts are linked explicitly by an administrator from Dashboard > Link Employee Accounts. This avoids allowing an unverified registration to claim another person's employee record.
- The employee must first register with an employee-role account. The administrator then links that login to the correct employee record.
- Admin-only actions remain protected by the existing `admin_required` decorator.

## Existing employee account linking
For older accounts where the email does not match, or where an employee row is already linked to another user, an administrator must correct the email/link manually. Example (confirm the IDs and email before running):
```sql
UPDATE employees
SET user_id = (SELECT id FROM users WHERE email = 'employee@example.com')
WHERE id = 12
  AND user_id IS NULL;
```

The admin account-linking screen is available at `/hr/account-linking` and lists unlinked employee records and unlinked employee-role login accounts.

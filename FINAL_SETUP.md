# Final HRMS setup and test guide

## Included modules
- Registration and login with employee/admin roles
- Admin dashboard and employee directory CRUD
- Employee account linking
- Employee self-service dashboard and profile
- Attendance management
- Leave requests and admin approval/rejection
- Payroll generation and employee payroll view
- CSV reports for employees, attendance and payroll

## Windows setup
1. Extract the ZIP and open the `employee_management` folder in VS Code.
2. Create a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and set your own `SECRET_KEY` and `DATABASE_URL`.
5. Ensure the PostgreSQL database exists and is accessible.
6. Start the application:
   ```powershell
   python run.py
   ```
7. Open `http://127.0.0.1:5000/login`.

## Important database notes
- The ZIP does not include your local PostgreSQL database, `.env`, or virtual environment.
- Your existing database records remain in PostgreSQL; extracting this ZIP does not change them.
- `db.create_all()` creates missing tables but is not a migration tool for changing existing columns.
- The project uses the tables `users`, `employees`, `attendance`, `leave_requests`, and `payroll`.
- Ensure every employee self-service account is linked to exactly one employee row through `employees.user_id`.
- New registrations are assigned the `employee` role. Do not allow public registration to create admin accounts.

## Demo payroll data
After confirming the `payroll` table exists and employees have salaries, run `database_seed/payroll_november_2026.sql` in pgAdmin Query Tool. It creates one illustrative November 2026 payroll row per salaried employee and skips existing employee/month rows. The allowance and deduction percentages are demo assumptions, not legal payroll rules.

## Demo employee login
The employee demo accounts created during setup were assigned the shared test password `Employee@123`. Change these passwords before any real use. Your admin password is not included in this package and is not changed by the setup instructions.

## Main URLs
- Login: `/login`
- Registration: `/register`
- Dashboard: `/dashboard`
- Employee directory: `/employees/`
- Account linking (admin): `/hr/account-linking`
- Attendance: `/hr/attendance`
- Leave management: `/hr/leaves`
- Payroll management (admin): `/hr/payroll`
- My profile (employee): `/hr/my-profile`
- My payroll (employee): `/hr/my-payroll`
- Employee CSV: `/hr/reports/employees.csv`
- Attendance CSV: `/hr/reports/attendance.csv`
- Payroll CSV: `/hr/reports/payroll.csv`

## Security and limitations
This is a development/portfolio project, not a production-ready payroll platform. Before production use, add CSRF protection, secure cookie configuration, rate limiting, audit logging, database backups, formal migrations, and comprehensive authorization tests. Validate payroll, tax, PF, ESI and other statutory calculations with qualified local guidance.


## Validation and security updates

This package includes server-side validation for registration, employee details, attendance, leave requests, account linking and payroll. It also enables Flask-WTF CSRF protection for POST forms. Browser-side HTML validation is an additional convenience only; the server remains authoritative.

### Password policy
New registrations require at least 10 characters, including uppercase and lowercase letters, a number and a special character. Existing passwords are not changed by this update.

### Install dependencies
After extracting the ZIP and activating your virtual environment, run:

```powershell
pip install -r requirements.txt
```

This installs Flask-WTF, which is required for CSRF protection. All POST forms include CSRF tokens. If you have an old browser tab open from before the update, refresh the page before submitting forms.

### Validation rules added
- Email format and maximum length checks; duplicate account and employee email checks.
- Name, department, designation, phone and comment length checks.
- Password complexity and length checks for new registrations.
- Salary must be finite, non-negative and have at most two decimal places.
- Attendance requires an existing employee, a valid status/date/time, no future date, and checkout later than check-in. Absent records cannot contain check-in/out times.
- Leave dates are checked, requests are limited to 91 calendar days, and overlapping pending/approved leave is rejected.
- Payroll validates month and monetary values, prevents deductions exceeding gross pay, and skips existing employee/month records.
- Account linking is restricted to administrators and employee-role accounts; an account or employee cannot be linked twice.
- CSRF protection is enabled on all POST forms; session cookies are HttpOnly and SameSite=Lax.

### Important deployment notes
This is a portfolio/demo application, not a certified production payroll system. Before public deployment, use HTTPS, set a strong unique SECRET_KEY, enable secure cookies behind HTTPS, add login rate limiting and audit logging, use database migrations (for example Alembic/Flask-Migrate), and have payroll/tax calculations reviewed for the relevant jurisdiction. Keep `.env` out of Git and never publish real employee data or passwords.

The project code was syntax-checked and templates were reviewed for CSRF fields. A live PostgreSQL end-to-end test was not performed in this packaging environment.

## Run with Docker (recommended for a portable demo)

Prerequisites: install and start Docker Desktop on Windows, then wait until it reports that Docker is running.

1. Copy `.env.docker.example` to `.env` in the project root.
2. Edit `.env` and set a long random `SECRET_KEY` and a strong `POSTGRES_PASSWORD`.
3. Open PowerShell in the folder containing `docker-compose.yml`.
4. Build and start both services:

   ```powershell
   docker compose up --build -d
   ```

5. Open `http://localhost:5000` (or the application's login URL).
6. View service status and logs:

   ```powershell
   docker compose ps
   docker compose logs -f web
   ```

7. Stop the services without deleting database data:

   ```powershell
   docker compose down
   ```

The PostgreSQL data is stored in the named Docker volume `postgres_data`, so it persists when containers are stopped or recreated. To stop and permanently delete that Docker database volume, use `docker compose down -v` (this deletes the Docker database data).

### Important: existing local PostgreSQL data

Docker creates a separate PostgreSQL database. It does not automatically copy the records from your existing Windows/pgAdmin database. If you want to keep your existing admin, employee accounts, attendance, leave and payroll records, export the existing database from pgAdmin (Custom or Plain backup) and restore it into the Docker PostgreSQL database. Do not run `docker compose down -v` after importing data unless you intend to erase that Docker database.

The application currently calls `db.create_all()` to create missing tables; this is not a replacement for database migrations when changing existing columns.

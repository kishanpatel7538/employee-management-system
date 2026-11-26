# Employee Management System (HRMS)

A Flask-based Employee Management System with role-based access for administrators and employees. It uses PostgreSQL for persistent storage and Docker Compose to run the web application and database.

## Features

### Authentication and access control
- User registration and login.
- Secure password hashing using Werkzeug.
- Flask-Login session management.
- Role-based access for administrators and employees.
- CSRF protection using Flask-WTF.

### Employee management
- Create, view, search and filter employee records.
- Update and delete employee records.
- Manage department, designation, salary and joining date.
- Link employee records to employee login accounts.

### HR operations
- Record and review attendance.
- Submit and approve or reject leave requests.
- Generate monthly payroll records.
- Employee self-service dashboard.
- View personal profile and payroll information.

### Reports
- Export employee records to CSV.
- Export attendance records to CSV.
- Export payroll records to CSV.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Database | PostgreSQL |
| ORM | Flask-SQLAlchemy |
| Authentication | Flask-Login |
| Security | Flask-WTF, Werkzeug |
| Database driver | Psycopg 3 |
| Containerization | Docker, Docker Compose |
| Frontend | HTML, CSS, JavaScript, Bootstrap (where used in templates) |

## Project Structure

```text
employee-management-system/
├── app/
│   ├── services/
│   ├── templates/
│   │   └── hr/
│   ├── __init__.py
│   ├── hr_routes.py
│   ├── models.py
│   ├── routes.py
│   └── validation.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── config.py
└── run.py
```

## Installation and Setup

### Prerequisites

- Python 3.10 or newer
- Docker Desktop
- Git

### Option 1: Run using Docker (Recommended)

**1. Clone the repository**

```bash
git clone https://github.com/kishanpatel7538/employee-management-system.git
cd employee-management-system
```

**2. Create your environment file**

PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Configure your own database password and Flask secret key in `.env`.

For Docker Compose, the database URL must use the Docker service hostname:

```text
postgresql+psycopg://postgres:<password>@db:5432/employee_db_restore
```

Ensure the database name, username and password match the PostgreSQL environment variables.

**3. Build and start containers**

```bash
docker compose up -d --build
```

**4. Access the application**

http://localhost:5000

**5. Check containers**

```bash
docker compose ps
```

**6. View application logs**

```bash
docker compose logs -f web
```

**7. Stop containers**

```bash
docker compose down
```

The PostgreSQL named volume is retained when containers are stopped. Avoid `docker compose down -v` unless you intentionally want to delete the database volume and its data.

### Option 2: Run locally using Python

**1. Create a virtual environment**

```bash
python -m venv venv
```

**2. Activate it on Windows**

```powershell
.\venv\Scripts\Activate.ps1
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure `.env`**

Use your local PostgreSQL connection details. When Flask runs directly on Windows and PostgreSQL is mapped to host port 5433, use `localhost:5433` in the database URL.

**5. Run Flask**

```bash
python run.py
```

Open http://localhost:5000.

## Database Design

The application uses five primary database models:

- **User:** Login credentials, password hash and role.
- **Employee:** Employee information and optional login account relationship.
- **Attendance:** Employee attendance records.
- **LeaveRequest:** Leave applications and administrative decisions.
- **Payroll:** Monthly payroll information.

An employee record can exist without a login account. The optional `employees.user_id` foreign key connects an employee profile to a user login.

## Security

- Environment variables are stored in `.env`.
- Passwords are stored as hashes.
- CSRF protection is enabled.
- Employee and administrator access is separated by role.
- Database credentials and private employee information must not be committed to GitHub.
- Use synthetic data when demonstrating the project.

## Future Improvements

- Automated unit and integration tests.
- GitHub Actions CI/CD pipeline.
- Admin management interface.
- Password reset functionality.
- Enhanced dashboard analytics.
- Application deployment to a cloud platform.

## Author

**Kishan Patel**

GitHub: https://github.com/kishanpatel7538

## License

No license has been specified yet. Standard copyright restrictions apply.
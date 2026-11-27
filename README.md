# Employee Management System (HRMS)

A full-stack Employee Management System built using **Python, Flask, and PostgreSQL**, designed to simplify employee administration and HR operations through role-based access.

The application provides separate interfaces for administrators and employees, supporting employee management, attendance tracking, leave management, payroll records, and CSV reporting.

## 🔗 Project Links

- **Live Application:** [Open Employee Management System](https://employee-management-system-mjfz.onrender.com)
- **GitHub Repository:** [View Source Code](https://github.com/kishanpatel7538/employee-management-system)

## 🚀 Key Features

### 1. Authentication and Access Control

- User registration and login.
- Secure password hashing using Werkzeug.
- Session management using Flask-Login.
- Role-based authorization for Admin and Employee accounts.
- CSRF protection using Flask-WTF.

### 2. Employee Management

- Add, view, update, and delete employee records.
- Search and filter employees.
- Manage employee departments and designations.
- Maintain salary and joining-date information.
- Link employee profiles with login accounts.

### 3. HR Management

- Record and manage employee attendance.
- Submit employee leave applications.
- Approve or reject leave requests.
- Generate monthly payroll records.
- Provide employee self-service functionality.

### 4. Employee Self-Service

- Employee dashboard.
- View personal profile information.
- Access payroll information.
- Submit leave requests.
- View attendance information.

### 5. Reports and Data Export

- Export employee records to CSV.
- Export attendance records to CSV.
- Export payroll records to CSV.

## 🛠️ Technology Stack

| Category             | Technologies                                  |
| -------------------- | --------------------------------------------- |
| Programming Language | Python                                        |
| Backend Framework    | Flask                                         |
| Database             | PostgreSQL                                    |
| ORM                  | Flask-SQLAlchemy                              |
| Authentication       | Flask-Login                                   |
| Security             | Werkzeug, Flask-WTF                           |
| Database Driver      | Psycopg 3                                     |
| Frontend             | HTML, CSS, JavaScript, Bootstrap (where used) |
| Containerization     | Docker, Docker Compose                        |
| Deployment           | Render                                        |
| Database Hosting     | Neon PostgreSQL                               |

## 🏗️ Project Architecture

```text
employee-management-system/
│
├── app/
│   ├── services/
│   ├── templates/
│   │   └── hr/
│   ├── __init__.py
│   ├── hr_routes.py
│   ├── models.py
│   ├── routes.py
│   └── validation.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── config.py
└── run.py
```

## 🗄️ Database Design

The application uses PostgreSQL with five primary database models.

| Model        | Description                                                |
| ------------ | ---------------------------------------------------------- |
| User         | Stores login credentials, password hashes, and user roles. |
| Employee     | Stores employee details and account relationships.         |
| Attendance   | Stores employee attendance records.                        |
| LeaveRequest | Stores leave applications and approval decisions.          |
| Payroll      | Stores monthly payroll information.                        |

**Database relationship:**

The `employees.user_id` foreign key connects an employee profile to its corresponding login account in the `users` table. This relationship supports employee self-service functionality.

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- Docker Desktop (for Docker deployment)
- Git

### Option 1: Run with Docker (Recommended)

**Step 1: Clone the repository**

```bash
git clone https://github.com/kishanpatel7538/employee-management-system.git

cd employee-management-system
```

**Step 2: Create the environment file**

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Configure the required environment variables in `.env`.

For Docker Compose, the database connection should use the PostgreSQL service hostname:

```text
postgresql+psycopg://postgres:<password>@db:5432/employee_db_restore
```

Make sure the database name, username, and password match your Docker Compose configuration.

**Step 3: Build and start the containers**

```bash
docker compose up -d --build
```

**Step 4: Open the application**

[http://localhost:5000](http://localhost:5000)

**Step 5: Check container status**

```bash
docker compose ps
```

**Step 6: View application logs**

```bash
docker compose logs -f web
```

**Step 7: Stop the containers**

```bash
docker compose down
```

Note: Docker's named PostgreSQL volume retains database data when containers are stopped. Avoid `docker compose down -v` unless you intentionally want to delete that data.

### Option 2: Run Locally Using Python

**Step 1: Create a virtual environment**

```bash
python -m venv venv
```

**Step 2: Activate the environment**

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

**Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 4: Configure environment variables**

Create a `.env` file using `.env.example` and configure your local PostgreSQL connection details.

If PostgreSQL is mapped to host port `5433`, use `localhost:5433` in your local database URL.

**Step 5: Start the application**

```bash
python run.py
```

Open:

[http://localhost:5000](http://localhost:5000)

## 🔐 Demo Login Credentials

Use the following demonstration accounts to explore the application.

### Employee Account

| Field    | Details                  |
| -------- | ------------------------ |
| Email    | `rahul.demo@example.com` |
| Password | `Demo@12345`             |
| Role     | Employee                 |

### Admin Account

Admin demonstration credentials should be configured separately before publication.

**Note:** Demo credentials are intended only for testing. Do not publish personal administrator credentials or use demonstration accounts for real employee data.

## 🔒 Security

- Passwords are stored using secure password hashing.
- Sensitive configuration is managed through environment variables.
- CSRF protection is enabled.
- Administrative routes enforce role-based access.
- Database credentials and secret keys must not be committed to GitHub.
- Synthetic data should be used for demonstrations.

## 🚀 Deployment

The application is deployed using:

- **Application Hosting:** Render
- **Database Hosting:** Neon PostgreSQL
- **Application Server:** Gunicorn

**Live URL:** [https://employee-management-system-mjfz.onrender.com](https://employee-management-system-mjfz.onrender.com)

## 🔮 Future Improvements

- Automated unit and integration testing.
- GitHub Actions CI/CD pipeline.
- Password reset functionality.
- Enhanced dashboard analytics.
- Improved employee notifications.
- Additional reporting and analytics features.

## 👨‍💻 Author

**Kishan Patel**

- GitHub: [kishanpatel7538](https://github.com/kishanpatel7538)

## 📄 License

No open-source license has been specified for this repository. Standard copyright restrictions apply.

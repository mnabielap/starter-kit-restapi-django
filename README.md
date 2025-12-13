# 🚀 Django REST Framework Starter Kit

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14-red.svg)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A production-ready **Django REST API boilerplate** designed to replicate the features of popular Regular starter kits but with the power and structure of Python/Django.

This project comes with **JWT Authentication**, **Role-Based Access Control**, **PostgreSQL/SQLite** support, **Docker** integration, and automated **API Documentation**.

---

## ✨ Features

*   **🐍 Core**: Django 4.2+ & Django REST Framework (DRF).
*   **💾 Database Agnostic**: Works with **SQLite** (default for dev) and **PostgreSQL** (production/docker).
*   **🔐 Authentication**: JWT Authentication using `djangorestframework-simplejwt` (Access & Refresh tokens).
*   **👤 User Management**: Custom User Model (Email-based login), Admin dashboard, and Role-based permissions (User vs Admin).
*   **🛡️ Security**: Password validation, CORS headers, standard security middlewares.
*   **📃 Documentation**: Auto-generated Swagger/OpenAPI 3.0 docs via `drf-spectacular`.
*   **🐳 Docker Ready**: Multi-stage build Dockerfile and persistent volume setup.
*   **🧪 Testing**: Integrated Unit Tests and custom Python script-based API tests (Postman replacement).
*   **⚙️ Best Practices**: structured `apps/` directory, environment variable configuration, and standardized error handling.

---

## 🛠️ Project Structure

```text
starter-kit-restapi-django/
├── .env.example             # Environment variables template
├── Dockerfile               # Production-ready Docker build
├── manage.py                # Django CLI
├── requirements.txt         # Python dependencies
├── api_tests/               # Custom Python scripts to test endpoints
│   ├── A1.auth_register.py  # Auth flow tests...
│   └── B1.user_create.py    # User flow tests...
├── config/                  # Main Project Settings
│   ├── settings.py
│   └── urls.py
└── apps/                    # Application Modules
    ├── common/              # Shared utilities (Exceptions, Pagination)
    └── users/               # Auth & User Logic (Models, Views, Serializers)
```

---

## ⚡ Getting Started (Local Development)

We recommended running the project locally first to understand the structure.

### 1. Prerequisites
*   Python 3.10 or higher
*   Git

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/mnabielap/starter-kit-restapi-django
cd starter-kit-restapi-django

# Create Virtual Environment
python -m venv venv

# Activate Virtual Environment
# Windows (CMD):
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy the example environment file. By default, this uses **SQLite**, so you don't need to install Postgres locally.

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

### 4. Database Setup
Apply migrations to create the database schema (SQLite file).

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User
Create a superuser to access the Django Admin Panel.

```bash
python manage.py createsuperuser
# Follow the prompts (Email, Password)
```

### 6. Run the Server
```bash
python manage.py runserver
```

The API is now running at `http://localhost:8000`.

---

## 📚 API Documentation & Testing

### Swagger UI
Once the server is running, visit:
👉 **[http://localhost:8000/v1/docs/](http://localhost:8000/v1/docs/)**

### Automated API Scripts (No Postman Needed!) 🚀
Instead of importing collections into Postman, this project includes Python scripts in `api_tests/` that hit the endpoints for you. They automatically save tokens to `secrets.json` so you don't need to copy-paste.

**How to use:**
1.  Make sure the server is running.
2.  Open a new terminal.
3.  Run the scripts in order:

```bash
# 1. Register a new user
python api_tests/A1.auth_register.py

# 2. Login (Saves token to secrets.json)
python api_tests/A2.auth_login.py

# 3. Get User Profile (Uses saved token)
python api_tests/B3.user_get_one.py
```
*Tip: Check the `api_tests/` folder for all available scenarios.*

---

## 🐳 Running with Docker (Production Mode)

Use this method to run the application in a containerized environment with a **PostgreSQL** database.

### 1. Prepare Environment
Create a specific environment file for Docker.

```bash
# Create .env.docker file
# Ensure DATABASE_URL matches the container name below (restapi-django-postgres)
```
**Content of `.env.docker`:**
```ini
PORT=5005
DEBUG=False
SECRET_KEY=change_me_in_prod
DATABASE_URL=postgres://hello_django:hello_django@restapi-django-postgres:5432/hello_django_db
JWT_ACCESS_EXPIRATION_MINUTES=30
```

### 2. Setup Network & Volumes
We need persistent storage for the DB and Media files, and a network for containers to talk to each other.

```bash
# Create Network
docker network create restapi_django_network

# Create Volumes
docker volume create restapi_django_db_volume
docker volume create restapi_django_media_volume
```

### 3. Start Database Container
Run PostgreSQL and attach it to the network and volume.

```bash
docker run -d \
  --name restapi-django-postgres \
  --network restapi_django_network \
  -v restapi_django_db_volume:/var/lib/postgresql/data \
  -e POSTGRES_USER=hello_django \
  -e POSTGRES_PASSWORD=hello_django \
  -e POSTGRES_DB=hello_django_db \
  --restart unless-stopped \
  postgres:15-alpine
```

### 4. Build & Run Application
Build the Django image and run it on port **5005**.

```bash
# Build the Image
docker build -t restapi-django-app .

# Run the Container
docker run -d -p 5005:5005 \
  --env-file .env.docker \
  --network restapi_django_network \
  -v restapi_django_media_volume:/app/media \
  --name restapi-django-container \
  --restart unless-stopped \
  restapi-django-app
```

The application is now accessible at: **http://localhost:5005**

---

## 🕹️ Docker Management Commands

Here are useful commands to manage your containers manually.

### 📜 View Logs
See what's happening inside the application container.
```bash
docker logs -f restapi-django-container
```

### 🛑 Stop Container
Stops the running application (does not delete data).
```bash
docker stop restapi-django-container
```

### ▶️ Start Container
Starts the container again if it was stopped.
```bash
docker start restapi-django-container
```

### 🗑️ Remove Container
To update the code, you often need to remove the container and run a new one.
```bash
docker stop restapi-django-container
docker rm restapi-django-container
```

### 📂 Manage Volumes
**View volumes:**
```bash
docker volume ls
```

**⚠️ Delete Volume (DANGER):**
This deletes your Database and Uploaded files permanently.
```bash
docker volume rm restapi_django_db_volume
docker volume rm restapi_django_media_volume
```

---

## 📝 Environment Variables

| Key | Description | Default (Dev) |
| :--- | :--- | :--- |
| `PORT` | Port for Docker/Gunicorn | `8000` |
| `DATABASE_URL` | Database Connection String | `sqlite:///db.sqlite3` |
| `DEBUG` | Django Debug Mode | `True` |
| `SECRET_KEY` | Django Secret Key | `unsafe-secret...` |
| `JWT_ACCESS_...` | JWT Expiration (Minutes) | `30` |
| `SMTP_...` | Email Server Config | `smtp.example.com` |

---

## 🤝 License

Distributed under the MIT License. See `LICENSE` for more information.
# Event Management Platform Backend

A backend service built using Django REST Framework for managing events, enrollments, facilitators, and seekers.

# Tech Stack

* Python 3.10
* Django 5.2
* Django REST Framework
* PostgreSQL
* JWT Authentication (SimpleJWT)
* Gmail SMTP

# Setup

## Clone Repository

git clone https://github.com/sreyas1818/event_platform
cd event_platform

## Create Virtual Environment

python -m venv venv

Activate environment:

Windows:

venv\Scripts\activate

Mac/Linux:

source venv/bin/activate

## Install Dependencies


pip install -r requirements.txt




# Environment Variables

Create a `.env` file in the project root.

```env
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password

```

# Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE events_db;
```

Update database configuration if needed.

Run migrations:


python manage.py makemigrations
python manage.py migrate

# Running Locally

Start the Django server:
python manage.py runserver
Application will be available at:

http://127.0.0.1:8000/


# API Overview

## Authentication
POST /auth/signup
POST /auth/verify-email
POST /auth/login
POST /auth/refresh


## Facilitator

GET    /events/my-events/
POST   /events/
PUT    /events/<id>/
DELETE /events/<id>/


## seeker
GET    /events/?page=<Page_Number>
GET    /events/<id>/
GET    /events/enrollments/upcoming/
GET    /events/enrollments/past/
POST   /events/<id>/enroll/
DELETE /events/<id>/enroll/


# Tests

The APIs were manually tested using Postman.

Test scenarios covered:

### Authentication

* Successful signup
* Duplicate email signup
* OTP verification
* Invalid OTP
* OTP expiry
* OTP attempt limit
* Login with verified user
* Login with unverified user

### Event Management

* Facilitator creates event
* Seeker attempts event creation
* Event update by creator
* Event update by non-creator
* Event deletion by creator
* Event deletion by non-creator

### Enrollment

* Successful enrollment
* Duplicate enrollment prevention
* Capacity validation
* Enrollment cancellation
* Upcoming enrollments
* Past enrollments

### Search & Filters

* Search by title
* Search by description
* Filter by language
* Filter by location
* Date range filtering
* Pagination
* Sorting

---

# Design Decisions

### Separate UserProfile Model

Role and verification status were stored in a separate UserProfile model rather than extending Django's built-in User model.

Benefits:

* Keeps authentication concerns separate
* Easier future extensibility
* Avoids custom user model complexity

---

### JWT Authentication

JWT was chosen over session-based authentication because:

* Better suited for REST APIs
* Stateless authentication
* Easy integration with frontend applications

---

### Soft Cancellation of Enrollments

Enrollment records are not deleted when cancelled.

Instead:

```text
ENROLLED -> CANCELLED
```

Benefits:

* Preserves enrollment history
* Supports auditing
* Enables future analytics

---

### Email Verification

Accounts remain inactive until OTP verification is completed.

Benefits:

* Prevents fake registrations
* Ensures valid email ownership

---

# Tradeoffs

### OTP Stored in Database

Current implementation stores OTPs in the database.

Pros:

* Simple implementation
* Easy expiration checks
* Easy attempt tracking

Cons:

* Additional database writes

For larger systems, Redis could be used instead.

---

### APIView Instead of ViewSets

APIView was chosen for clarity and explicit control over permissions and business logic.

Pros:

* Easier to understand
* Better control of custom flows

Cons:

* More boilerplate code

---

### Manual Role Checks

Role checks are currently implemented directly in views.

Pros:

* Simple and explicit

Cons:

* Repeated logic across endpoints

A larger project would benefit from custom permission classes.

---

# Security Features

Implemented:

* JWT Authentication
* Role-Based Access Control
* OTP Expiry (5 Minutes)
* OTP Attempt Limiting
* Email Verification
* email when seeker enrolls into event

---

# Future Improvements

* Docker deployment
* Swagger/OpenAPI documentation
* Automated test suite
* Celery for scheduled emails
* Reminder emails before events

---

# Author

Sreyas

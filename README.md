# PacePower 🏃‍♂️

A web application built with Django and PostgreSQL that allows users to log their runs, manage personal heart rate zones, plan training sessions, and view training calendars.

---

## ✨ Features

- 📝 Log runs with date, type, distance, pace, HR and notes
- ❤️ Manage personal heart rate zones in user profile
- 📅 Create training plans and schedule planned runs
- 🗓️ View monthly training calendar
- 🏷️ Tag runs for easier filtering
- 🔐 Register/login/logout functionality
- 🛠️ Admin interface to manage data
- 📚 Documented models, views, forms, and URLs
- 🧪 Unit tests with Pytest

---

## 🛠️ Technologies

- 🐍 Python 3.12
- 🌐 Django 5.2.4
- 🗄️ PostgreSQL
- 🎨 HTML/CSS
- 🧪 Pytest

---

## ⚙️ Setup

1. **Clone the repo**
   `git clone https://github.com/yourusername/pacepower.git`

2. **Create and activate virtual environment**
   `python -m venv env && source env/bin/activate`

3. **Install dependencies**
   `pip install -r requirements.txt`

4. **Configure PostgreSQL**
   Create database and user as described in `settings.py`

5. **Run migrations**
   `python manage.py migrate`

6. **Start the development server**
   `python manage.py runserver`

7. **Access the app**
   👉 Visit `http://127.0.0.1:8000/`

---

## 🚀 Future improvements

- ✅ Marking planned runs as completed
- 📊 Weekly, monthly, and yearly mileage statistics
- 🧬 Advanced indicators such as VO₂max and training load
- 💪 Adding a new Power app for strength training
- ⌚ Importing workout data from smartwatches
- 🤖 AI-assisted progressive overload workout generation
- 🎨 Wrapping everything into a modern, responsive frontend

---

## 🧪 Running tests

```bash
pytest

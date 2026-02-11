# Mawa3id — Appointment Booking Platform

**Mawa3id** is a full-stack web application that allows clients to discover businesses, book appointments, and leave reviews, while business owners can manage services, availability, and customer bookings.
This project was built as a **portfolio project to demonstrate full‑stack development skills with Django, databases, authentication, and real-world application design.**

---

## 🌐 Live Demo
> _Add your deployed link here (Render, Railway, Heroku, etc.)_

---

## ✨ Key Features

### 👤 User Authentication & Roles
- Secure user registration and login
- Role-based access (Client vs Business Owner)
- User profiles with images

### 🏢 Business Management (Business Owners)
- Create and manage business profiles
- Add and edit services
- Create and manage available time slots
- View dashboard with bookings and reviews

### 📅 Booking System (Clients)
- Browse businesses by category
- View available services and time slots
- Book appointments with businesses

### ⭐ Reviews & Ratings
- Clients can leave ratings and feedback
- Businesses can view customer reviews

---

## 🛠️ Tech Stack

**Backend**
- Python 3
- Django 6
- Django ORM

**Frontend**
- HTML5, CSS3
- Django Templates

**Database**
- PostgreSQL

**Tools & Workflow**
- Git & GitHub (Team collaboration, branching, PRs)
- Environment variables with `.env`

---

## 📸 Screenshots
> _Add screenshots of your app here (home page, dashboard, booking flow)_

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/AliFahmi07/Mawa3id.git
cd Mawa3id
```

### 2️⃣ Create a Virtual Environment
```bash
pipenv shell
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Variables
Create a `.env` file in the root directory:
```env
DB_NAME="YOUR_DATABASE_NAME"
DB_USERNAME="YOUR_USER_NAME"
DB_PASSWORD="YOUR_PASSWORD"
DB_PORT="YOUR_DATABASE_PORT"
```

---

## 🗄️ Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## ▶️ Run the Application
```bash
python manage.py runserver
```
Visit:
```
http://127.0.0.1:8000/
```

---

## 📂 Project Structure
```text
Mawa3id/
│── main_app/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   ├── static/
│── mawa3id/          # Django project settings
│── manage.py
│── requirements.txt
│── .env
```

---

## 🧑‍💻 Development Workflow

### Create a Feature Branch
```bash
git checkout -b feature/your-feature
```

### Update Your Branch with Main
```bash
git checkout main
git pull origin main
git checkout feature/your-feature
git merge main
```

---

## 🐛 Common Issues & Fixes

### Missing Database Columns
```bash
python manage.py makemigrations
python manage.py migrate
```

### Merge Conflicts
Resolve conflicts manually, then:
```bash
git add .
git commit
```

---

## 🚀 Future Enhancements
- Online payments integration (Stripe)
- Real-time notifications
- Admin analytics dashboard
- Mobile app version (React Native / Flutter)
- Calendar sync (Google Calendar)

---

## 👨‍💻 Team members

**Ali Shamlooh**
Software Engineer | Full Stack Developer
[GitHub Profile](https://github.com/Ali19Shamlooh)
**Ali Fahmi**
Software Engineer | Full Stack Developer
[GitHub Profile](https://github.com/AliFahmi07)
**Ammar Shabib**
Software Engineer | Full Stack Developer
[GitHub Profile](https://github.com/ammarys-w)
**Abdulla Khamis**
Software Engineer | Full Stack Developer
[GitHub Profile](https://github.com/3bdulla03)

---

## 📜 License
This project is for educational and portfolio purposes.


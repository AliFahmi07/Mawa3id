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
- HTML5, CSS3, JavaScript  
- Django Templates

**Database**  
- PostgreSQL (Production)  
- SQLite (Development)

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
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Variables
Create a `.env` file in the root directory:
```env
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
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

## 👨‍💻 Author

**Ali Shamlooh**  
Software Engineer | Django Developer  
> Add your LinkedIn / GitHub profile link here

---

## 📜 License
This project is for educational and portfolio purposes.


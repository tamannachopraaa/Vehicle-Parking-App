# 🚗 Vehicle Parking App - V1

A multi-user parking management system for 4-wheeler vehicle parking built using Flask and SQLite. The app allows Admins to manage parking lots and spots, while registered Users can reserve and release parking spaces.

---

## 📌 Project Description

The **Vehicle Parking App** is designed to streamline the process of managing multiple parking lots and booking parking spots. It supports two roles:

- **Admin** (superuser): Can create/edit/delete parking lots, manage parking spots, and view system-wide reports.
- **User**: Can register/login, book the first available parking spot in a chosen lot, and release it after use.

This app was developed as part of the **Modern Application Development I (MAD I)** course project.

---

## 🛠️ Tech Stack Used

| Layer        | Technology             |
|--------------|------------------------|
| Backend      | Flask (Python)         |
| Frontend     | HTML, CSS, Jinja2      |
| Styling      | Bootstrap 5            |
| Database     | SQLite (via SQLAlchemy)|
| Charts       | Chart.js (for summary) |

---

## 👥 User Roles and Dashboards

### 🔐 Admin Dashboard
- Predefined admin user (no registration required)
- Create and manage parking lots
- Auto-create parking spots based on lot capacity
- View spot status (Occupied/Available)
- Delete parking lots (only if all spots are empty)
- View all registered users
- View graphical summaries of lot usage

### 👤 User Dashboard
- Register/Login functionality
- View all available parking lots
- Auto-assign first available parking spot
- Release the spot when vehicle leaves
- See timestamps for parking in/out
- View personal parking history summary

---


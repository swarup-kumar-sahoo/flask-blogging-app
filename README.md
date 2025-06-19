
```
# 📝 Flask Blogging App — LabTalks

LabTalks is a simple and modern blogging application built using **Flask**. It allows users to view science news posts, add blogs, and explore scientific discoveries in a clean, responsive interface.
![Screenshot 2025-06-19 113442](https://github.com/user-attachments/assets/705cbb36-581b-4238-b0f4-e566837ee5b5)
---

## 🚀 Features

- View scientific blogs and news updates
- Add, edit, and delete posts (admin)
- Responsive design (HTML/CSS/Tailwind)
- MySQL database support
- User-friendly interface

---

## 🛠️ Tech Stack

- **Backend:** Python (Flask)
- **Frontend:** HTML, CSS (Tailwind)
- **Database:** MySQL

---

## 📂 Project Structure

```

/flask-blog-app
├── app.py
├── templates/
│    └── index.html
│    └── display.html
│    └── login.html
│    └── register.html
│    └── update.html
│    └── viewmore.html
├── static/
│    └── css/
└── README.md

````

---

## ⚡ Installation

1️⃣ Clone the repo:
```bash
git clone https://github.com/your-username/flask-blog-app.git
cd flask-blog-app
````

2️⃣ Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3️⃣ Install dependencies:

| Package                                      | Purpose                                                                                  |
| -------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Flask**                                    | The core web framework                                                                   |
| **flask-mysqldb**                            | Flask extension to connect with MySQL                                                    |
| **MySQLdb** (via `mysqlclient`)              | MySQL database driver                                                                    |
| **python-dotenv** (optional but recommended) | For loading secrets/env variables (if you plan to move `secret_key`, DB creds to `.env`) |
| **Flask-WTF** (optional)                     | If you later add form validation helpers                                                 |
| **Werkzeug**                                 | Comes with Flask, used for session security, etc.                                        |


4️⃣ Run the app:

```bash
python app.py
```
---

## 📌 Usage

* Open `http://127.0.0.1:5000/` in your browser.
* Browse blogs, add new posts (if admin).
* Expand with features like login, comments, tags.

---

# 🌐 Skill Swap  

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)  
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask)  
![MySQL](https://img.shields.io/badge/Database-MySQL-blue?logo=mysql)  
![TailwindCSS](https://img.shields.io/badge/Styling-TailwindCSS-38bdf8?logo=tailwind-css)  
![Status](https://img.shields.io/badge/Project-Active-brightgreen)  

Skill Swap is a web platform where people can **exchange skills** instead of money.  
You can offer what you know and learn what you don’t — all within a simple and interactive app.  

---

## ✨ Features
- 👤 **User Profiles** – create and manage your skill profile  
- 🔄 **Skill Swapping** – request and exchange skills with others  
- 🔍 **Search & Match** – find people based on skills and availability  
- 🌓 **Dark/Light Mode** – toggle between themes for better usability  
- 📍 **Location (Optional)** – share your city if you want local matches  

---

## 🛠 Tech Stack
**Frontend**  
- HTML, CSS, JavaScript  
- TailwindCSS (styling)  

**Backend**  
- Python (Flask)  
- Flask-SQLAlchemy (ORM)  
- Flask-WTF (forms)  

**Database**  
- MySQL (via MySQL Workbench)  

---

## 🚀 Getting Started
Follow these steps to run the project locally.

### 1. Clone the repository
```bash
git clone https://github.com/priy07/skill-swap.git
cd skill-swap
```

### 2. Set up Python environment
```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
pip install -r requirements.txt
```

### 3. Install Node dependencies
```bash
npm install
```

### 4. Start the Flask server
```bash
python app.py
```
Now open http://127.0.0.1:5000 in your browser.

## 📂 Project Structure
```bash
skill_swap/
│── app.py                # Flask app entry
│── requirements.txt       # Python dependencies
│── package.json           # Node dependencies
│── tailwind.config.js     # Tailwind config
│── templates/             # HTML templates
│── static/
│   ├── css/               # Styles (input.css, output.css)
│   ├── logo/              # Logos/images
│   └── src/               # JS or other assets
```
## 📸 Screenshots
<img width="1819" height="836" alt="Screenshot 2025-08-19 231341" src="https://github.com/user-attachments/assets/1adb5f64-a75d-44c5-9f04-f2a9e842470a" />
<img width="1919" height="1079" alt="Screenshot 2025-08-19 231147" src="https://github.com/user-attachments/assets/86eda0c4-5119-4c7f-96bf-b518547ed423" />
<img width="1822" height="846" alt="Screenshot 2025-08-19 232415" src="https://github.com/user-attachments/assets/ec76a0e4-2312-46c0-aa54-fe51fb3dc4aa" />
<img width="1918" height="877" alt="Screenshot 2025-08-19 232344" src="https://github.com/user-attachments/assets/d83a4ffb-b4f1-4337-9630-56c5012ea8b7" />

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first to discuss your idea.

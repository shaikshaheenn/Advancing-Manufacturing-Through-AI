# Advancing-Manufacturing-Through-AI
A full-stack Django web application that demonstrates the application of Artificial Intelligence in modern manufacturing industries.
The platform integrates Machine Learning models, Gemini AI (gemini-2.5-flash), and data-driven dashboards to solve key challenges in manufacturing operations.

Project Overview

This platform provides manufacturing companies, researchers, and industry analysts with AI-powered tools for:

Predicting machine failures before they occur

Detecting product defects using computer vision

Optimizing production processes with AI-generated recommendations

Assessing supply chain risks automatically

Generating intelligent reports and strategic insights using Gemini AI

Features
AI Applications

Predictive Maintenance

Random Forest model predicts machine failure using sensor data such as:

Temperature

Vibration

Pressure

Runtime hours

Quality Control

Manual defect reporting system

Optional ResNet18 image-based AI severity detection

Process Optimization

Rule-based AI engine generates context-aware recommendations

Recommendations are based on process name and efficiency data

Supply Chain Risk

Gradient Boosting model predicts supplier risk levels

Uses five input features to determine risk probability

Gemini AI Integration (gemini-2.5-flash)

Recommendations

AI-generated adoption recommendations for manufacturing topics

Challenge Analysis

Detailed 7-point analysis of manufacturing challenges

Report Summaries

Automatic executive summaries for admin reports

Dashboard Insights

Live AI-generated insights based on platform statistics

User Management

Custom session-based authentication (without Django default auth)

Role-based access system including:

Admin

Industry User

Researcher

Analyst

Admin panel for managing:

Users

Content

Reports

System monitoring

Profile management with password update functionality

Dashboard & Analytics

Real-time statistics across all AI modules

Role-specific navigation (Admin vs User)

Responsive dashboard interface

Mobile-friendly sidebar navigation

Tech Stack
Layer	Technology
Backend	Python 3.11, Django 4.x
Database	MySQL (via mysqlclient)
ML Models	scikit-learn, joblib, numpy
AI Vision	PyTorch, torchvision, Pillow
Gemini AI	google-genai (gemini-2.5-flash)
Frontend	Bootstrap 5.3, Bootstrap Icons, Chart.js
Fonts	Google Fonts — Inter
Environment	python-decouple (.env)
Installation & Setup
Create and Activate Virtual Environment
python -m venv AI_venv
Windows
AI_venv\Scripts\activate
Linux / Mac
source AI_venv/bin/activate
Install Dependencies
pip install -r requirements.txt
Create MySQL Database
CREATE DATABASE ai_manufacturing_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
Run Migrations
python manage.py makemigrations
python manage.py migrate
Train AI Models
Train Predictive Maintenance Model (Random Forest)
python ai_models/train_model.py
Train Supply Chain Risk Model (Gradient Boosting)
python ai_models/train_supply_model.py
Seed Sample Data
python seed_data.py
Start the Server
python manage.py runserver

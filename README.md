
#  Income Spending Survey Tool  

A **Flask web application** for collecting and analyzing user income and spending data, developed to support **healthcare product launch analysis**.  

---

##  Project Overview  

This application collects **user demographic and financial data** to analyze spending patterns across categories, with a strong focus on **healthcare spending insights**.  

- Initially developed **locally** to avoid early cloud costs  
- Later enhanced with a **CI/CD pipeline** for automated deployment to **AWS EC2**  
- Once code is pushed to GitHub, the workflow:  
  - Provisions/updates the application  
  - Configures Gunicorn + Nginx  
  - Exposes the app via a public IP for browser access  

Survey submissions are stored in **MongoDB Atlas**, while **CSV exports** are automatically saved in the project directory.  

ℹ *Some unnecessary files were unstaged to keep the repo clean. A folder of **screenshots** is included to demonstrate database persistence and analysis outputs in case the live instance isn’t running.*  

---

##  Features  

-  **Web Form** – Collects age, gender, income, and expense data  
-  **Data Storage** – MongoDB Atlas integration (with CSV fallback)  
-  **Data Processing** – Python class for calculations and analysis  
-  **Visualization** – Automated chart generation for insights  
-  **Export Functionality** – Export survey data to CSV  
-  **CI/CD Enabled** – Automated AWS deployment from GitHub  
---
##  Project Structure  

income-spending-survey/
├── app.py # Main Flask application
├── user_class.py # User data processing class
├── requirements.txt # Development dependencies
├── requirements-prod.txt # Production dependencies
├── user_data.csv # Data storage (CSV fallback)
├── templates/
│ └── index.html # Survey form
├── analysis/ # Generated visualizations
└── static/ # Static files

---

##  Data Collection

The application collects the following:

- **Demographic Data**  
  - Age  
  - Gender  

- **Financial Data**  
  - Total Income  

- **Expense Categories**  
  - Utilities (electricity, water, gas)  
  - Entertainment (dining out, movies, hobbies)  
  - School/Education Fees  
  - Shopping (clothing, personal items)  
  - Healthcare (medicines, doctor visits)  

---

##  Installation & Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd income-spending-survey

## Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

you can only use this when you are working in an enviroment that isnt fully supported with the kind of python instalations needed for this work  you dont really need it when working on aws terminal but you need it when working locally

pip install -r requirements.txt
sudo apt install mongodb
sudo systemctl start mongodb
## Run the application

python app.py

## Production Deployment (AWS)

This project uses CI/CD deployment pipelines to automate AWS deployment.

## Steps:

Launch an EC2 instance (Ubuntu Server).

Connect to the instance via SSH.

Push changes to your GitHub repository.

GitHub Actions workflow automatically:

Installs dependencies

Deploys the app to EC2

Configures Gunicorn + Nginx

Restarts services

Makes the application available via public IP
## API Endpoints

/ – Main survey form

/submit – Form submission (POST)

/success – Success page after submission

/export – Export data to CSV

/analysis – View data analysis and visualizations

## Data Analysis

The application automatically generates:

Average Income by Age chart

Spending by Gender across categories

Summary statistics of collected data

## Deployment Details

The application is configured for production with:

Gunicorn WSGI server

Systemd for service management

Nginx as a reverse proxy

MongoDB for persistent data storage

## Usage

Open your browser and visit the server’s public IP.

Fill out the survey form and submit responses.

Access data insights at:

/analysis for charts

/export for CSV downloads

## Requirements

Python 3.6+

MongoDB

Nginx (production only)

## screenshort atachment
through some process which cannot stay longer a place like my instance which i can not leave for long do to charges
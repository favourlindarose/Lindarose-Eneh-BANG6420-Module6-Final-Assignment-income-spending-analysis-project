from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import certifi  # Import certifi for SSL certificate handling

app = Flask(__name__)

# =====================================
# Initialize MongoDB Atlas with SSL fix
# =====================================
client = None
db = None
collection = None

try:
    # Get Mongo URI from environment or default to Atlas
    mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://kingsamuel412_db_user:5YmyvqhPpiksB4QJ@favour.k47oqe4.mongodb.net/?retryWrites=true&w=majority&appName=favour")
    
    # Connect with SSL certificate fix
    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=10000,  # Increased timeout
        tls=True,  # Explicitly enable TLS
        tlsAllowInvalidCertificates=False,  # Don't allow invalid certs
        tlsCAFile=certifi.where()  # Use certifi's CA bundle
    )
    
    client.server_info()  # Force connection test
    db = client['user_data_db']
    collection = db['users']
    print(f"✅ Successfully connected to MongoDB Atlas with SSL")
    
except Exception as e:
    print(f"❌ Could not connect to MongoDB Atlas: {e}")
    collection = None
    print("📂 Falling back to CSV storage")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
    age = request.form['age']
    gender = request.form['gender']
    total_income = request.form['total_income']

    # Get expense values (use 0 if empty)
    utilities = request.form.get('utilities', 0) or 0
    entertainment = request.form.get('entertainment', 0) or 0
    school_fees = request.form.get('school_fees', 0) or 0
    shopping = request.form.get('shopping', 0) or 0
    healthcare = request.form.get('healthcare', 0) or 0

    # Prepare data
    user_data = {
        'age': int(age),
        'gender': gender,
        'total_income': float(total_income),
        'expenses': {
            'utilities': float(utilities),
            'entertainment': float(entertainment),
            'school_fees': float(school_fees),
            'shopping': float(shopping),
            'healthcare': float(healthcare)
        },
        'timestamp': datetime.now()
    }

    # Save to MongoDB if available, else CSV
    if collection is not None:
        try:
            collection.insert_one(user_data)
            print("✅ Data saved to MongoDB")
        except Exception as e:
            print(f"❌ Error saving to MongoDB: {e}")
            save_to_csv(user_data)
    else:
        save_to_csv(user_data)

    return redirect(url_for('success'))

def save_to_csv(user_data):
    """Save data to CSV file"""
    csv_file = 'user_data.csv'
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'age', 'gender', 'total_income',
                      'utilities', 'entertainment', 'school_fees',
                      'shopping', 'healthcare']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'timestamp': user_data['timestamp'],
            'age': user_data['age'],
            'gender': user_data['gender'],
            'total_income': user_data['total_income'],
            'utilities': user_data['expenses']['utilities'],
            'entertainment': user_data['expenses']['entertainment'],
            'school_fees': user_data['expenses']['school_fees'],
            'shopping': user_data['expenses']['shopping'],
            'healthcare': user_data['expenses']['healthcare']
        })

    print("📂 Data saved to CSV")

@app.route('/success')
def success():
    return """
    <div style="text-align: center; padding: 50px;">
        <h2>Thank You!</h2>
        <p>Your response has been recorded.</p>
        <a href='/'>Submit another response</a>
        <br><br>
        <a href='/export'>Export data to CSV</a>
        <br><br>
        <a href='/analysis'>View Data Analysis</a>
    </div>
    """

@app.route('/export')
def export_data():
    if collection is not None:
        try:
            all_data = collection.find()
            export_to_csv(all_data)
            return "✅ Data exported to user_data.csv"
        except Exception as e:
            return f"❌ MongoDB error: {e}. Data is being saved to CSV."
    else:
        return "ℹ Data is being saved directly to CSV (user_data.csv)"

def export_to_csv(all_data):
    with open('user_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['age', 'gender', 'total_income', 'utilities',
                      'entertainment', 'school_fees', 'shopping', 'healthcare']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for data in all_data:
            writer.writerow({
                'age': data['age'],
                'gender': data['gender'],
                'total_income': data['total_income'],
                'utilities': data['expenses']['utilities'],
                'entertainment': data['expenses']['entertainment'],
                'school_fees': data['expenses']['school_fees'],
                'shopping': data['expenses']['shopping'],
                'healthcare': data['expenses']['healthcare']
            })

def get_data():
    """Retrieve data from MongoDB or CSV"""
    data = []

    if collection is not None:
        try:
            mongo_data = list(collection.find({}, {'_id': 0}))
            if mongo_data:
                return mongo_data
        except Exception as e:
            print(f"❌ Error retrieving data from MongoDB: {e}")

    csv_file = 'user_data.csv'
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                data.append({
                    'age': row['age'],
                    'gender': row['gender'],
                    'total_income': row['total_income'],
                    'expenses': {
                        'utilities': row.get('utilities', 0),
                        'entertainment': row.get('entertainment', 0),
                        'school_fees': row.get('school_fees', 0),
                        'shopping': row.get('shopping', 0),
                        'healthcare': row.get('healthcare', 0)
                    }
                })
        except Exception as e:
            print(f"❌ Error reading CSV file: {e}")

    return data

def generate_visualizations():
    """Generate charts and return them as base64 images"""
    plot_urls = {}

    try:
        data = get_data()
        if not data:
            return plot_urls

        df = pd.DataFrame(data)
        df['total_spending'] = df['expenses'].apply(lambda x: sum(x.values()))
        df['savings'] = df['total_income'] - df['total_spending']

        # Income vs Spending
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=df, x='total_income', y='total_spending', s=100, ax=ax)
        ax.set_title('Income vs Spending')
        ax.set_xlabel('Income ($)')
        ax.set_ylabel('Spending ($)')
        plot_urls['income_vs_spending'] = fig_to_base64(fig)
        plt.close(fig)

        # Age Distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(df['age'], bins=10, kde=True, ax=ax)
        ax.set_title('Age Distribution of Respondents')
        ax.set_xlabel('Age')
        ax.set_ylabel('Count')
        plot_urls['age_distribution'] = fig_to_base64(fig)
        plt.close(fig)

        # Gender Distribution
        fig, ax = plt.subplots(figsize=(8, 6))
        gender_counts = df['gender'].value_counts()
        gender_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_title('Gender Distribution')
        ax.set_ylabel('')
        plot_urls['gender_distribution'] = fig_to_base64(fig)
        plt.close(fig)

        # Spending by Category
        fig, ax = plt.subforms(figsize=(12, 6))
        categories = ['utilities', 'entertainment', 'school_fees', 'shopping', 'healthcare']
        avg_expenses = [df['expenses'].apply(lambda x: x[cat]).mean() for cat in categories]
        bars = ax.bar(categories, avg_expenses)
        ax.set_title('Average Spending by Category')
        ax.set_ylabel('Average Amount ($)')
        ax.set_xlabel('Category')

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:.2f}',
                   ha='center', va='bottom')

        plot_urls['spending_by_category'] = fig_to_base64(fig)
        plt.close(fig)

        # Income Distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(df['total_income'], bins=8, kde=True, ax=ax)
        ax.set_title('Income Distribution')
        ax.set_xlabel('Income ($)')
        ax.set_ylabel('Count')
        plot_urls['income_distribution'] = fig_to_base64(fig)
        plt.close(fig)

    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")

    return plot_urls

def fig_to_base64(fig):
    """Convert matplotlib figure to base64"""
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf-8')

@app.route('/analysis')
def analysis():
    plot_urls = generate_visualizations()
    data = get_data()
    stats = {}

    if data:
        df = pd.DataFrame(data)
        df['total_spending'] = df['expenses'].apply(lambda x: sum(x.values()))

        stats = {
            'total_responses': len(df),
            'avg_income': df['total_income'].mean(),
            'avg_spending': df['total_spending'].mean(),
            'avg_age': df['age'].mean(),
            'gender_counts': df['gender'].value_counts().to_dict()
        }

    return render_template('analysis.html', plot_urls=plot_urls, stats=stats)

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')

    app.run(debug=False, host='0.0.0.0', port=5000)
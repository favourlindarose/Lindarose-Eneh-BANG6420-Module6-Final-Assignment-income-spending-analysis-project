import csv
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from datetime import datetime

class User:
    def __init__(self, age, gender, total_income, utilities, entertainment, school_fees, shopping, healthcare):
        self.age = age
        self.gender = gender
        self.total_income = total_income
        self.utilities = utilities
        self.entertainment = entertainment
        self.school_fees = school_fees
        self.shopping = shopping
        self.healthcare = healthcare
    
    def calculate_total_expenses(self):
        return self.utilities + self.entertainment + self.school_fees + self.shopping + self.healthcare
    
    def calculate_savings(self):
        return self.total_income - self.calculate_total_expenses()
    
    def to_dict(self):
        return {
            'age': self.age,
            'gender': self.gender,
            'total_income': self.total_income,
            'utilities': self.utilities,
            'entertainment': self.entertainment,
            'school_fees': self.school_fees,
            'shopping': self.shopping,
            'healthcare': self.healthcare,
            'total_expenses': self.calculate_total_expenses(),
            'savings': self.calculate_savings()
        }
    
    @classmethod
    def load_from_csv(cls, filename='user_data.csv'):
        users = []
        try:
            with open(filename, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    user = cls(
                        age=int(row['age']),
                        gender=row['gender'],
                        total_income=float(row['total_income']),
                        utilities=float(row['utilities']),
                        entertainment=float(row['entertainment']),
                        school_fees=float(row['school_fees']),
                        shopping=float(row['shopping']),
                        healthcare=float(row['healthcare'])
                    )
                    users.append(user)
            print(f"Loaded {len(users)} users from {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found. Starting with empty user list.")
        except Exception as e:
            print(f"Error loading CSV: {e}")
        return users
    
    @classmethod
    def analyze_data(cls, filename='user_data.csv'):
        try:
            # Load data into pandas DataFrame
            df = pd.read_csv(filename)
            
            # Create analysis directory if it doesn't exist
            import os
            if not os.path.exists('analysis'):
                os.makedirs('analysis')
            
            # Set style for better looking plots
            plt.style.use('default')
            sns.set_palette("husl")
            
            # 1. Show ages with the highest income
            plt.figure(figsize=(12, 6))
            age_income = df.groupby('age')['total_income'].mean().sort_values(ascending=False)
            age_income.plot(kind='bar', color='lightcoral')
            plt.title('Average Income by Age', fontsize=16, fontweight='bold')
            plt.xlabel('Age', fontsize=12)
            plt.ylabel('Average Income ($)', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.savefig('analysis/age_income.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # 2. Show gender distribution across spending categories
            gender_expenses = df.groupby('gender')[['utilities', 'entertainment', 'school_fees', 'shopping', 'healthcare']].mean()
            
            plt.figure(figsize=(14, 8))
            gender_expenses.plot(kind='bar')
            plt.title('Average Spending by Gender Across Categories', fontsize=16, fontweight='bold')
            plt.xlabel('Gender', fontsize=12)
            plt.ylabel('Average Spending ($)', fontsize=12)
            plt.xticks(rotation=0)
            plt.legend(title='Expense Categories', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.savefig('analysis/gender_spending.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # 3. Create a summary report
            summary = df.describe()
            summary.to_csv('analysis/summary_statistics.csv')
            
            # 4. Additional visualizations
            # Income distribution
            plt.figure(figsize=(10, 6))
            plt.hist(df['total_income'], bins=20, color='skyblue', edgecolor='black', alpha=0.7)
            plt.title('Income Distribution', fontsize=16, fontweight='bold')
            plt.xlabel('Income ($)', fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.grid(alpha=0.3)
            plt.tight_layout()
            plt.savefig('analysis/income_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print("Analysis complete! Charts saved in the 'analysis' folder.")
            return df
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Load users from CSV
    users = User.load_from_csv()
    
    # Print information about each user
    for user in users:
        print(f"Age: {user.age}, Gender: {user.gender}, Income: ${user.total_income:,.2f}")
        print(f"Total Expenses: ${user.calculate_total_expenses():,.2f}")
        print(f"Savings: ${user.calculate_savings():,.2f}")
        print("-" * 40)
    
    # Perform data analysis and create visualizations
    User.analyze_data()
import pandas as pd
import os

# Path to Excel file
EXCEL_PATH = os.path.join('quiz_data', 'results.xlsx')

def init_database():
    """Initialize the Excel database if it doesn't exist"""
    if not os.path.exists('quiz_data'):
        os.makedirs('quiz_data')
    
    if not os.path.exists(EXCEL_PATH):
        df = pd.DataFrame(columns=['Name', 'Email', 'Category', 'Score', 'Date'])
        df.to_excel(EXCEL_PATH, index=False)

def save_result(name, email, category, score):
    """Save quiz result to Excel"""
    init_database()
    
    # Read existing data
    df = pd.read_excel(EXCEL_PATH)
    
    # Add new result
    new_result = pd.DataFrame({
        'Name': [name],
        'Email': [email],
        'Category': [category],
        'Score': [score],
        'Date': [pd.Timestamp.now()]
    })
    
    # Combine and save
    df = pd.concat([df, new_result], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False)
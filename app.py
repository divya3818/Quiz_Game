from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'quiz_secret_key_2023'

# Quiz categories and questions
quiz_data = {
    "science": [
        {
            "question": "What is the chemical symbol for gold?",
            "options": ["Go", "Gd", "Au", "Ag"],
            "answer": "Au"
        },
        {
            "question": "Which planet is known as the Red Planet?",
            "options": ["Venus", "Mars", "Jupiter", "Saturn"],
            "answer": "Mars"
        },
        {
            "question": "What is the largest organ in the human body?",
            "options": ["Liver", "Heart", "Skin", "Lungs"],
            "answer": "Skin"
        },
        {
            "question": "What is the main gas found in Earth's atmosphere?",
            "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"],
            "answer": "Nitrogen"
        },
        {
            "question": "What is the hardest natural substance on Earth?",
            "options": ["Gold", "Iron", "Diamond", "Platinum"],
            "answer": "Diamond"
        }
    ],
    "history": [
        {
            "question": "In which year did World War II end?",
            "options": ["1943", "1945", "1947", "1950"],
            "answer": "1945"
        },
        {
            "question": "Who was the first President of the United States?",
            "options": ["Thomas Jefferson", "John Adams", "George Washington", "Benjamin Franklin"],
            "answer": "George Washington"
        },
        {
            "question": "Which ancient civilization built the Machu Picchu?",
            "options": ["Aztec", "Maya", "Inca", "Egyptian"],
            "answer": "Inca"
        },
        {
            "question": "Who was the first woman to win a Nobel Prize?",
            "options": ["Marie Curie", "Rosalind Franklin", "Dorothy Crowfoot Hodgkin", "Maria Goeppert-Mayer"],
            "answer": "Marie Curie"
        },
        {
            "question": "Which year did the Titanic sink?",
            "options": ["1912", "1915", "1920", "1905"],
            "answer": "1912"
        }
    ],
    "technology": [
        {
            "question": "What does CPU stand for?",
            "options": ["Central Processing Unit", "Computer Personal Unit", "Central Processor Unit", "Central Process Unit"],
            "answer": "Central Processing Unit"
        },
        {
            "question": "Which company created the iPhone?",
            "options": ["Microsoft", "Samsung", "Apple", "Google"],
            "answer": "Apple"
        },
        {
            "question": "What is the main purpose of RAM in a computer?",
            "options": ["Long-term storage", "Processing power", "Temporary memory", "Graphics rendering"],
            "answer": "Temporary memory"
        },
        {
            "question": "What does HTML stand for?",
            "options": ["Hyper Text Markup Language", "High Tech Modern Language", "Hyper Transfer Markup Language", "Home Tool Markup Language"],
            "answer": "Hyper Text Markup Language"
        },
        {
            "question": "Which programming language is known as the 'language of the web'?",
            "options": ["Python", "Java", "JavaScript", "C++"],
            "answer": "JavaScript"
        }
    ]
}

# Initialize Excel database
def init_database():
    if not os.path.exists('quiz_data'):
        os.makedirs('quiz_data')
    
    excel_path = os.path.join('quiz_data', 'quiz_results.xlsx')
    if not os.path.exists(excel_path):
        df = pd.DataFrame(columns=['Name', 'Email', 'Category', 'Score', 'Date'])
        df.to_excel(excel_path, index=False)

# Save results to Excel
def save_to_excel(name, email, category, score):
    init_database()
    excel_path = os.path.join('quiz_data', 'quiz_results.xlsx')
    
    try:
        df = pd.read_excel(excel_path)
    except:
        df = pd.DataFrame(columns=['Name', 'Email', 'Category', 'Score', 'Date'])
    
    new_data = {
        'Name': [name],
        'Email': [email],
        'Category': [category],
        'Score': [score],
        'Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    }
    
    new_df = pd.DataFrame(new_data)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_excel(excel_path, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_quiz', methods=['GET', 'POST'])
def start_quiz():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        category = request.form['category']
        
        session['user'] = {
            'name': name,
            'email': email,
            'category': category,
            'score': 0,
            'current_question': 0
        }
        
        # Save user info to Excel immediately
        save_to_excel(name, email, category, 0)
        
        return redirect(url_for('quiz'))
    
    return render_template('start_quiz.html', categories=quiz_data.keys())

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_data = session['user']
    category = user_data['category']
    current_question = user_data['current_question']
    
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        correct_answer = quiz_data[category][current_question]['answer']
        
        if user_answer == correct_answer:
            user_data['score'] += 1
        
        user_data['current_question'] += 1
        session['user'] = user_data
        
        if user_data['current_question'] >= len(quiz_data[category]):
            # Update Excel with final score
            save_to_excel(user_data['name'], user_data['email'], category, user_data['score'])
            return redirect(url_for('results'))
        else:
            return redirect(url_for('quiz'))
    
    if current_question >= len(quiz_data[category]):
        return redirect(url_for('results'))
    
    question_data = quiz_data[category][current_question]
    return render_template('quiz.html', 
                         question=question_data, 
                         question_num=current_question + 1, 
                         total_questions=len(quiz_data[category]),
                         category=category)

@app.route('/results')
def results():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_data = session['user']
    category = user_data['category']
    score = user_data['score']
    total = len(quiz_data[category])
    
    # Clear session data
    session.pop('user', None)
    
    return render_template('results.html', score=score, total=total, category=category)

@app.route('/progress')
def progress():
    try:
        excel_path = os.path.join('quiz_data', 'quiz_results.xlsx')
        df = pd.read_excel(excel_path)
        return render_template('progress.html', results=df.to_dict('records'))
    except:
        return render_template('progress.html', results=[])

if __name__ == '__main__':
    init_database()
    app.run(debug=True, port=5000)
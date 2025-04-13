from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import jwt
import datetime
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)
SECRET_KEY = "ваш_секретний_ключ"

# Ініціалізація бази даних
def init_db():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Таблиця користувачів
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    
    # Таблиця книг
    c.execute('''CREATE TABLE IF NOT EXISTS books
                (id INTEGER PRIMARY KEY, title TEXT, author TEXT, genre TEXT, 
                 year INTEGER, description TEXT, available BOOLEAN)''')
    
    # Таблиця запитів на книги
    c.execute('''CREATE TABLE IF NOT EXISTS book_requests
                (id INTEGER PRIMARY KEY, user_id INTEGER, book_id INTEGER, 
                 status TEXT, request_date TEXT)''')
    
    # Таблиця оцінок книг
    c.execute('''CREATE TABLE IF NOT EXISTS ratings
                (id INTEGER PRIMARY KEY, user_id INTEGER, book_id INTEGER, 
                 rating INTEGER, comment TEXT)''')
    
    # Таблиця повідомлень чату
    c.execute('''CREATE TABLE IF NOT EXISTS chat_messages
                (id INTEGER PRIMARY KEY, from_user_id INTEGER, to_user_id INTEGER, 
                 message TEXT, timestamp TEXT)''')
    
    # Таблиця історії книг користувача
    c.execute('''CREATE TABLE IF NOT EXISTS user_book_history
                (id INTEGER PRIMARY KEY, user_id INTEGER, book_id INTEGER, timestamp TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# Функції аутентифікації
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Перевірка чи користувач вже існує
    c.execute("SELECT * FROM users WHERE username = ?", (data['username'],))
    if c.fetchone():
        conn.close()
        return jsonify({"message": "Користувач вже існує"}), 400
    
    # Додавання нового користувача
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
              (data['username'], data['password'], data['role']))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Реєстрація успішна"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
              (data['username'], data['password']))
    user = c.fetchone()
    conn.close()
    
    if user:
        token = jwt.encode({
            'user_id': user[0],
            'username': user[1],
            'role': user[3],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY)
        
        return jsonify({"token": token, "user_id": user[0], "role": user[3]}), 200
    else:
        return jsonify({"message": "Неправильне ім'я користувача або пароль"}), 401

# Функції роботи з книгами
@app.route('/books', methods=['GET'])
def get_books():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = "SELECT * FROM books"
    params = []
    
    # Додавання фільтрів
    if request.args.get('title'):
        query += " WHERE title LIKE ?"
        params.append(f"%{request.args.get('title')}%")
    
    if request.args.get('author'):
        if 'WHERE' in query:
            query += " AND author LIKE ?"
        else:
            query += " WHERE author LIKE ?"
        params.append(f"%{request.args.get('author')}%")
    
    if request.args.get('genre'):
        if 'WHERE' in query:
            query += " AND genre = ?"
        else:
            query += " WHERE genre = ?"
        params.append(request.args.get('genre'))
    
    # Додавання сортування
    if request.args.get('sort'):
        query += f" ORDER BY {request.args.get('sort')}"
        if request.args.get('order'):
            query += f" {request.args.get('order')}"
    
    c.execute(query, params)
    books = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify({"books": books}), 200

@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO books (title, author, genre, year, description, available) 
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (data['title'], data['author'], data['genre'], 
               data['year'], data['description'], True))
    
    conn.commit()
    book_id = c.lastrowid
    conn.close()
    
    return jsonify({"message": "Книгу додано", "book_id": book_id}), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    c.execute('''UPDATE books SET title = ?, author = ?, genre = ?, 
                 year = ?, description = ?, available = ? WHERE id = ?''',
              (data['title'], data['author'], data['genre'], data['year'], 
               data['description'], data['available'], book_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Книгу оновлено"}), 200

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Книгу видалено"}), 200

# Маршрути для запитів на книги
@app.route('/book_requests', methods=['POST'])
def create_book_request():
    data = request.get_json()
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO book_requests (user_id, book_id, status, request_date) 
                 VALUES (?, ?, ?, ?)''',
              (data['user_id'], data['book_id'], 'pending', 
               datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    request_id = c.lastrowid
    conn.close()
    
    return jsonify({"message": "Запит створено", "request_id": request_id}), 201

@app.route('/book_requests', methods=['GET'])
def get_book_requests():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Отримуємо всі запити на книги
    c.execute('''SELECT br.*, b.title as book_title, u.username as user_name 
                 FROM book_requests br
                 JOIN books b ON br.book_id = b.id
                 JOIN users u ON br.user_id = u.id
                 ORDER BY br.request_date DESC''')
    
    requests = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify({"requests": requests}), 200

@app.route('/book_requests/<int:request_id>', methods=['PUT'])
def update_book_request(request_id):
    data = request.get_json()
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    c.execute("UPDATE book_requests SET status = ? WHERE id = ?",
              (data['status'], request_id))
    
    # Якщо запит схвалено, додаємо до історії користувача
    if data['status'] == 'approved':
        c.execute("SELECT user_id, book_id FROM book_requests WHERE id = ?", (request_id,))
        user_id, book_id = c.fetchone()
        
        c.execute('''INSERT INTO user_book_history (user_id, book_id, timestamp)
                     VALUES (?, ?, ?)''',
                  (user_id, book_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Статус запиту оновлено"}), 200

# Маршрути для оцінок та коментарів
@app.route('/ratings', methods=['POST'])
def add_rating():
    data = request.get_json()
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO ratings (user_id, book_id, rating, comment) 
                 VALUES (?, ?, ?, ?)''',
              (data['user_id'], data['book_id'], data['rating'], data.get('comment', '')))
    
    conn.commit()
    rating_id = c.lastrowid
    conn.close()
    
    return jsonify({"message": "Оцінку додано", "rating_id": rating_id}), 201

# Маршрути для чату
@app.route('/chat', methods=['POST'])
def send_message():
    data = request.get_json()
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO chat_messages (from_user_id, to_user_id, message, timestamp) 
                 VALUES (?, ?, ?, ?)''',
              (data['from_user_id'], data['to_user_id'], data['message'], 
               datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    message_id = c.lastrowid
    conn.close()
    
    return jsonify({"message": "Повідомлення надіслано", "message_id": message_id}), 201

@app.route('/chat/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''SELECT * FROM chat_messages 
                 WHERE (from_user_id = ? OR to_user_id = ?) 
                 ORDER BY timestamp''', (user_id, user_id))
    
    messages = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify({"messages": messages}), 200

# Система рекомендацій на основі машинного навчання
@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Отримуємо останні 3 книги користувача
    c.execute('''SELECT b.* FROM books b
                 JOIN user_book_history h ON b.id = h.book_id
                 WHERE h.user_id = ?
                 ORDER BY h.timestamp DESC LIMIT 3''', (user_id,))
    
    recent_books = [dict(row) for row in c.fetchall()]
    
    # Якщо у користувача немає історії книг, повертаємо популярні книги
    if not recent_books:
        c.execute('''SELECT b.* FROM books b
                     JOIN ratings r ON b.id = r.book_id
                     GROUP BY b.id
                     ORDER BY AVG(r.rating) DESC LIMIT 5''')
        recommendations = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify({"recommendations": recommendations, "method": "popular"}), 200
    
    # Отримуємо всі книги для рекомендацій
    c.execute("SELECT * FROM books")
    all_books = [dict(row) for row in c.fetchall()]
    
    # Створюємо DataFrame для обробки
    books_df = pd.DataFrame(all_books)
    
    # Комбінуємо атрибути для рекомендації
    books_df['content'] = books_df['title'] + ' ' + books_df['author'] + ' ' + books_df['genre'] + ' ' + books_df['description']
    
    # Використовуємо TF-IDF для створення векторів особливостей
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(books_df['content'])
    
    # Обчислюємо схожість косинусів
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Знаходимо індекси останніх книг користувача
    indices = [books_df[books_df['id'] == book['id']].index[0] for book in recent_books]
    
    # Розраховуємо середню схожість для всіх книг
    sim_scores = []
    for i in range(len(cosine_sim)):
        if i in indices:  # Пропускаємо книги, які вже прочитані
            continue
        score = sum(cosine_sim[idx][i] for idx in indices) / len(indices)
        sim_scores.append((i, score))
    
    # Сортуємо книги за схожістю
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Отримуємо індекси книг з найвищим рейтингом схожості
    book_indices = [i[0] for i in sim_scores[:5]]
    
    # Повертаємо рекомендовані книги
    recommendations = books_df.iloc[book_indices].to_dict(orient='records')
    
    conn.close()
    
    return jsonify({"recommendations": recommendations, "method": "content_based"}), 200

if __name__ == '__main__':
    app.run(debug=True)

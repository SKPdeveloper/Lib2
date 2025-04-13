import streamlit as st
import requests
import pandas as pd
import time
from PIL import Image

# Кольорова гама
PRIMARY_COLOR = "#9A1750"  # бордовий
SECONDARY_COLOR = "#E3AFBC"  # світло-рожевий
ACCENT_COLOR = "#EE4C7C"  # яскраво-рожевий
BG_COLOR = "#F5E6E8"  # дуже світло-рожевий
TEXT_COLOR = "#5D001E"  # темно-бордовий
CONTRAST_TEXT = "#FFFFFF"  # білий для контрастного тексту

# Конфігурація сторінки
st.set_page_config(
    page_title="Бібліотечна система",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS для налаштування кольорів, анімацій та єдиного розміру кнопок
st.markdown(f"""
<style>
    /* Загальні стилі */
    .stApp {{
        background-color: {BG_COLOR};
    }}
    
    /* Стилі для кнопок */
    .stButton>button {{
        background-color: {PRIMARY_COLOR};
        color: {CONTRAST_TEXT};
        width: 100%;
        height: 2.5rem;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        background-color: {ACCENT_COLOR};
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }}
    
    /* Стилі для текстових полів */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        border-color: {PRIMARY_COLOR};
        border-radius: 5px;
        transition: all 0.3s ease;
    }}
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
        border-color: {ACCENT_COLOR};
        box-shadow: 0 0 0 2px rgba(154, 23, 80, 0.2);
    }}
    
    /* Стилі для заголовків і тексту */
    h1, h2, h3, h4, h5, h6 {{
        color: {PRIMARY_COLOR};
        font-weight: bold;
    }}
    
    p, li {{
        color: {TEXT_COLOR};
        line-height: 1.6;
    }}
    
    /* Стилі для карток і контейнерів */
    .book-card {{
        background-color: {SECONDARY_COLOR};
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    .book-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }}
    
    .recommendation-card {{
        background-color: {ACCENT_COLOR};
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: {CONTRAST_TEXT};
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    .recommendation-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }}
    
    .chat-message-me {{
        background-color: {SECONDARY_COLOR};
        padding: 12px; 
        border-radius: 15px 15px 3px 15px; 
        margin-bottom: 10px;
        color: {TEXT_COLOR};
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    .chat-message-other {{
        background-color: {PRIMARY_COLOR};
        padding: 12px; 
        border-radius: 15px 15px 15px 3px; 
        margin-bottom: 10px;
        color: {CONTRAST_TEXT};
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    /* Стилі для бічної панелі */
    .sidebar .sidebar-content {{
        background-color: {SECONDARY_COLOR};
        padding: 20px;
        border-radius: 0 10px 10px 0;
    }}
    
    /* Стилі для вкладок */
    .tab-content {{
        padding: 20px;
        border: 1px solid #ddd;
        border-top: none;
        border-radius: 0 0 5px 5px;
        background-color: white;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        white-space: pre-wrap;
        background-color: {SECONDARY_COLOR};
        border-radius: 5px 5px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {PRIMARY_COLOR};
        color: white;
    }}
    
    /* Спеціальний клас для відступів */
    .margin-top {{
        margin-top: 20px;
    }}
    
    .margin-bottom {{
        margin-bottom: 20px;
    }}
    
    /* Клас для аватарок */
    .avatar {{
        border-radius: 50%;
        overflow: hidden;
        border: 3px solid {PRIMARY_COLOR};
    }}
</style>
""", unsafe_allow_html=True)

# URL сервера API
API_URL = "http://localhost:5000"

# Функції для роботи з API
def register_user(username, password, role):
    response = requests.post(
        f"{API_URL}/register",
        json={"username": username, "password": password, "role": role}
    )
    return response.json(), response.status_code

def login_user(username, password):
    response = requests.post(
        f"{API_URL}/login",
        json={"username": username, "password": password}
    )
    return response.json(), response.status_code

def get_books(filters=None, sort=None, order=None):
    params = {}
    if filters:
        params.update(filters)
    if sort:
        params["sort"] = sort
    if order:
        params["order"] = order
    
    response = requests.get(f"{API_URL}/books", params=params)
    return response.json(), response.status_code

def add_book(title, author, genre, year, description):
    response = requests.post(
        f"{API_URL}/books",
        json={
            "title": title,
            "author": author,
            "genre": genre,
            "year": year,
            "description": description,
            "available": True
        }
    )
    return response.json(), response.status_code

def update_book(book_id, title, author, genre, year, description, available):
    response = requests.put(
        f"{API_URL}/books/{book_id}",
        json={
            "title": title,
            "author": author,
            "genre": genre,
            "year": year,
            "description": description,
            "available": available
        }
    )
    return response.json(), response.status_code

def delete_book(book_id):
    response = requests.delete(f"{API_URL}/books/{book_id}")
    return response.json(), response.status_code

def create_book_request(user_id, book_id):
    response = requests.post(
        f"{API_URL}/book_requests",
        json={"user_id": user_id, "book_id": book_id}
    )
    return response.json(), response.status_code

def update_book_request(request_id, status):
    response = requests.put(
        f"{API_URL}/book_requests/{request_id}",
        json={"status": status}
    )
    return response.json(), response.status_code

def add_rating(user_id, book_id, rating, comment):
    response = requests.post(
        f"{API_URL}/ratings",
        json={
            "user_id": user_id,
            "book_id": book_id,
            "rating": rating,
            "comment": comment
        }
    )
    return response.json(), response.status_code

def send_message(from_user_id, to_user_id, message):
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "message": message
        }
    )
    return response.json(), response.status_code

def get_messages(user_id):
    response = requests.get(f"{API_URL}/chat/{user_id}")
    return response.json(), response.status_code

def get_recommendations(user_id):
    response = requests.get(f"{API_URL}/recommendations/{user_id}")
    return response.json(), response.status_code

def get_book_requests():
    response = requests.get(f"{API_URL}/book_requests")
    return response.json(), response.status_code

# Ініціалізація стану сесії
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Функції для навігації
def navigate_to(page):
    st.session_state.page = page

def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.page = 'login'

# Сторінка входу/реєстрації
def auth_page():
    st.markdown("<h1 style='text-align: center;'>📚 Бібліотечна система</h1>", unsafe_allow_html=True)
    
    # Створюємо вкладки для входу та реєстрації
    tab1, tab2 = st.tabs(["📝 Вхід", "✨ Реєстрація"])
    
    with tab1:
        # Форма входу
        with st.form(key="login_form"):
            username = st.text_input("Ім'я користувача")
            password = st.text_input("Пароль", type="password")
            
            submit_button = st.form_submit_button(label="Увійти")
            
            if submit_button:
                if username and password:
                    with st.spinner("Перевірка облікових даних..."):
                        time.sleep(0.5)  # Імітація завантаження
                        response, status_code = login_user(username, password)
                    
                    if status_code == 200:
                        st.session_state.logged_in = True
                        st.session_state.user_id = response["user_id"]
                        st.session_state.username = username
                        st.session_state.role = response["role"]
                        st.session_state.page = 'catalog'
                        st.success("✅ Вхід успішний!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ " + response["message"])
                else:
                    st.error("❌ Будь ласка, заповніть всі поля")
    
    with tab2:
        # Форма реєстрації
        with st.form(key="register_form"):
            reg_username = st.text_input("Ім'я користувача")
            reg_password = st.text_input("Пароль", type="password")
            reg_role = st.selectbox("Роль", ["reader", "librarian"], 
                                    format_func=lambda x: "Читач" if x == "reader" else "Бібліотекар")
            
            submit_button = st.form_submit_button(label="Зареєструватися")
            
            if submit_button:
                if reg_username and reg_password:
                    with st.spinner("Створення облікового запису..."):
                        time.sleep(0.5)  # Імітація завантаження
                        response, status_code = register_user(reg_username, reg_password, reg_role)
                    
                    if status_code == 201:
                        st.success("✅ Реєстрація успішна! Тепер ви можете увійти.")
                    else:
                        st.error("❌ " + response["message"])
                else:
                    st.error("❌ Будь ласка, заповніть всі поля")
    
    # Декоративний елемент внизу сторінки
    st.markdown("""
    <div style='margin-top: 50px; text-align: center;'>
        <p>Ласкаво просимо до нашої бібліотечної системи!</p>
        <p>Тут ви можете знайти, замовити та оцінити книги, а також отримати рекомендації.</p>
    </div>
    """, unsafe_allow_html=True)

# Сторінка каталогу
def catalog_page():
    st.markdown("<h1 style='text-align: center;'>Каталог книг</h1>", unsafe_allow_html=True)
    
    # Фільтрація та сортування
    with st.expander("📋 Фільтри та сортування", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            title_filter = st.text_input("Назва містить:")
            author_filter = st.text_input("Автор містить:")
        
        with col2:
            genre_filter = st.text_input("Жанр:")
        
        with col3:
            sort_by = st.selectbox("Сортувати за:", 
                                  ["title", "author", "year", "genre"],
                                  format_func=lambda x: {"title": "Назвою", "author": "Автором", "year": "Роком", "genre": "Жанром"}[x])
            sort_order = st.selectbox("Порядок:", ["ASC", "DESC"], format_func=lambda x: "За зростанням" if x == "ASC" else "За спаданням")
        
        filters = {}
        if title_filter:
            filters["title"] = title_filter
        if author_filter:
            filters["author"] = author_filter
        if genre_filter:
            filters["genre"] = genre_filter
    
    # Отримання списку книг
    with st.spinner("Завантаження книг..."):
        books_response, status_code = get_books(filters, sort_by, sort_order)
    
    if status_code == 200:
        books = books_response.get("books", [])
        
        if not books:
            st.info("📭 Книги не знайдено.")
        else:
            st.success(f"📚 Знайдено {len(books)} книг")
            # Відображення книг у вигляді карток
            cols = st.columns(3)
            for i, book in enumerate(books):
                with cols[i % 3]:
                    with st.container():
                        st.markdown(f"""
                        <div class="book-card">
                            <h3>{book['title']}</h3>
                            <p><strong>Автор:</strong> {book['author']}</p>
                            <p><strong>Жанр:</strong> {book['genre']}</p>
                            <p><strong>Рік:</strong> {book['year']}</p>
                            <p><strong>Статус:</strong> {"✅ Доступна" if book['available'] else "❌ Недоступна"}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("📖 Деталі", key=f"details_{book['id']}"):
                            st.session_state.selected_book = book
                            navigate_to('book_details')
                            st.rerun()
                        
                        if st.session_state.role == "reader" and book['available']:
                            if st.button("📩 Замовити", key=f"request_{book['id']}"):
                                with st.spinner("Створення запиту..."):
                                    response, status = create_book_request(
                                        st.session_state.user_id, book['id'])
                                if status == 201:
                                    st.success("✅ Запит на книгу створено!")
                                else:
                                    st.error("❌ " + response["message"])
    else:
        st.error("❌ Помилка при отриманні книг")
    
    # Якщо користувач є бібліотекарем, показуємо кнопку додавання книги
    if st.session_state.role == "librarian":
        st.markdown("<div class='margin-top'></div>", unsafe_allow_html=True)
        if st.button("➕ Додати нову книгу", key="add_new_book"):
            navigate_to('add_book')
            st.rerun()
    
    # Якщо користувач є читачем, показуємо рекомендації
    if st.session_state.role == "reader":
        st.markdown("<div class='margin-top'></div>", unsafe_allow_html=True)
        with st.expander("🌟 Рекомендовані книги", expanded=True):
            with st.spinner("Підбираємо рекомендації..."):
                recommendations, status = get_recommendations(st.session_state.user_id)
            
            if status == 200:
                recommended_books = recommendations.get("recommendations", [])
                method = recommendations.get("method", "")
                
                if method == "popular":
                    st.info("ℹ️ Ці рекомендації базуються на популярних книгах")
                else:
                    st.info("ℹ️ Ці рекомендації базуються на ваших останніх книгах")
                
                if not recommended_books:
                    st.info("📭 Немає рекомендацій")
                else:
                    cols = st.columns(len(recommended_books))
                    for i, book in enumerate(recommended_books):
                        with cols[i]:
                            st.markdown(f"""
                            <div class="recommendation-card">
                                <h4>{book['title']}</h4>
                                <p><strong>Автор:</strong> {book['author']}</p>
                                <p><strong>Жанр:</strong> {book['genre']}</p>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.error("❌ Помилка при отриманні рекомендацій")

# Сторінка деталей книги
def book_details_page():
    if 'selected_book' not in st.session_state:
        st.error("❌ Книга не вибрана")
        if st.button("↩️ Повернутися до каталогу"):
            navigate_to('catalog')
            st.rerun()
        return
    
    book = st.session_state.selected_book
    
    st.markdown(f"<h1>{book['title']}</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="book-card">
            <p><strong>Автор:</strong> {book['author']}</p>
            <p><strong>Жанр:</strong> {book['genre']}</p>
            <p><strong>Рік:</strong> {book['year']}</p>
            <p><strong>Статус:</strong> {"✅ Доступна" if book['available'] else "❌ Недоступна"}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("📝 Опис")
        st.write(book['description'])
    
    # Якщо користувач є читачем, показуємо форму оцінки
    if st.session_state.role == "reader":
        st.markdown("<div class='margin-top'></div>", unsafe_allow_html=True)
        st.markdown("<div class='highlight'><h3>Залишити відгук</h3></div>", unsafe_allow_html=True)
        
        with st.form(key="rating_form"):
            rating = st.slider("⭐ Оцінка", 1, 5, 5)
            comment = st.text_area("💬 Коментар")
            
            submit_button = st.form_submit_button(label="📤 Надіслати відгук")
            
            if submit_button:
                if comment:
                    with st.spinner("Надсилання відгуку..."):
                        response, status = add_rating(
                            st.session_state.user_id, book['id'], rating, comment)
                    
                    if status == 201:
                        st.success("✅ Відгук додано!")
                    else:
                        st.error("❌ " + response["message"])
                else:
                    st.warning("⚠️ Будь ласка, додайте коментар до вашої оцінки")
    
    # Якщо користувач є бібліотекарем, показуємо форму редагування
    if st.session_state.role == "librarian":
        st.markdown("<div class='margin-top'></div>", unsafe_allow_html=True)
        st.markdown("<div class='highlight'><h3>Редагувати книгу</h3></div>", unsafe_allow_html=True)
        
        with st.form(key="edit_book_form"):
            new_title = st.text_input("📚 Назва", value=book['title'])
            new_author = st.text_input("✍️ Автор", value=book['author'])
            new_genre = st.text_input("🏷️ Жанр", value=book['genre'])
            new_year = st.number_input("📅 Рік", value=book['year'])
            new_description = st.text_area("📝 Опис", value=book['description'])
            new_available = st.checkbox("✅ Доступна", value=book['available'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                update_button = st.form_submit_button(label="🔄 Оновити")
            
            with col2:
                delete_button = False  # Ми використаємо окрему форму для видалення
            
            if update_button:
                if new_title and new_author and new_genre:
                    with st.spinner("Оновлення книги..."):
                        response, status = update_book(
                            book['id'], new_title, new_author, new_genre, 
                            new_year, new_description, new_available)
                    
                    if status == 200:
                        st.success("✅ Книгу оновлено!")
                        # Оновлюємо дані книги в session_state
                        st.session_state.selected_book = {
                            "id": book['id'],
                            "title": new_title,
                            "author": new_author,
                            "genre": new_genre,
                            "year": new_year,
                            "description": new_description,
                            "available": new_available
                        }
                        st.rerun()
                    else:
                        st.error("❌ " + response["message"])
                else:
                    st.error("❌ Заповніть обов'язкові поля: назва, автор, жанр")
        
        # Окрема форма для видалення книги
        if st.session_state.role == "librarian":
            with st.form(key="delete_book_form"):
                st.warning("⚠️ Видалення книги - незворотна дія!")
                confirm = st.checkbox("Підтверджую, що хочу видалити цю книгу", key="confirm_delete")
                
                delete_button = st.form_submit_button(label="🗑️ Видалити книгу")
                
                if delete_button:
                    if confirm:
                        with st.spinner("Видалення книги..."):
                            response, status = delete_book(book['id'])
                        if status == 200:
                            st.success("✅ Книгу видалено!")
                            time.sleep(1)
                            navigate_to('catalog')
                            st.rerun()
                        else:
                            st.error("❌ " + response["message"])
                    else:
                        st.error("❌ Будь ласка, підтвердіть видалення")
    
    st.markdown("<div class='margin-top'></div>", unsafe_allow_html=True)
    if st.button("↩️ Повернутися до каталогу"):
        navigate_to('catalog')
        st.rerun()

# Сторінка додавання книги (тільки для бібліотекаря)
def add_book_page():
    if st.session_state.role != "librarian":
        st.error("❌ У вас немає прав для доступу до цієї сторінки")
        if st.button("↩️ Повернутися до каталогу"):
            navigate_to('catalog')
            st.rerun()
        return
    
    st.markdown("<h1>Додати нову книгу</h1>", unsafe_allow_html=True)
    
    with st.form(key="add_book_form"):
        title = st.text_input("📚 Назва")
        author = st.text_input("✍️ Автор")
        genre = st.text_input("🏷️ Жанр")
        year = st.number_input("📅 Рік", min_value=1000, max_value=2030, value=2023)
        description = st.text_area("📝 Опис")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit_button = st.form_submit_button(label="➕ Додати книгу")
        
        with col2:
            cancel_button = st.form_submit_button(label="❌ Скасувати")
        
        if submit_button:
            if title and author and genre and description:
                with st.spinner("Додавання книги..."):
                    response, status = add_book(title, author, genre, year, description)
                
                if status == 201:
                    st.success("✅ Книгу додано!")
                    time.sleep(1)
                    navigate_to('catalog')
                    st.rerun()
                else:
                    st.error("❌ " + response["message"])
            else:
                st.warning("⚠️ Будь ласка, заповніть всі обов'язкові поля")
        
        if cancel_button:
            navigate_to('catalog')
            st.rerun()

# Сторінка чату
def chat_page():
    st.markdown(f"<h1>{'Чат з бібліотекарем' if st.session_state.role == 'reader' else 'Чат з читачами'}</h1>", unsafe_allow_html=True)
    
    # Отримання списку повідомлень
    with st.spinner("Завантаження повідомлень..."):
        response, status = get_messages(st.session_state.user_id)
    
    if status == 200:
        messages = response.get("messages", [])
        
        # Якщо користувач є бібліотекарем, групуємо повідомлення за користувачами
        if st.session_state.role == "librarian":
            # Отримання списку читачів, з якими є повідомлення
            user_ids = set()
            for msg in messages:
                if msg["from_user_id"] != st.session_state.user_id:
                    user_ids.add(msg["from_user_id"])
                if msg["to_user_id"] != st.session_state.user_id:
                    user_ids.add(msg["to_user_id"])
            
            if not user_ids:
                st.info("📭 У вас немає повідомлень")
            else:
                # Відображення чатів з користувачами
                selected_user = st.selectbox(
                    "👤 Виберіть користувача",
                    list(user_ids),
                    format_func=lambda x: f"Користувач {x}"
                )
                
                # Фільтрація повідомлень для вибраного користувача
                user_messages = [
                    msg for msg in messages 
                    if (msg["from_user_id"] == selected_user and msg["to_user_id"] == st.session_state.user_id) or
                       (msg["from_user_id"] == st.session_state.user_id and msg["to_user_id"] == selected_user)
                ]
                
                display_chat(user_messages, selected_user)
        else:
            # Фільтрація повідомлень для бібліотекарів (для користувача з роллю "reader")
            librarian_messages = [
                msg for msg in messages 
                if msg["from_user_id"] != st.session_state.user_id or msg["to_user_id"] != st.session_state.user_id
            ]
            
            if not librarian_messages:
                st.info("📭 У вас немає повідомлень з бібліотекарем")
                st.markdown("""
                <div style='text-align: center; margin-top: 30px;'>
                    <p>Почніть діалог, надіславши своє перше повідомлення!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                display_chat(librarian_messages, None)
    else:
        st.error("❌ Помилка при отриманні повідомлень")
    
    st.markdown("<div class='margin-top'></div>", unsafe_allow_html=True)
    if st.button("↩️ Повернутися до каталогу"):
        navigate_to('catalog')
        st.rerun()

# Функція для відображення чату
def display_chat(messages, to_user_id):
    # Контейнер для повідомлень з фіксованою висотою і прокруткою
    chat_container = st.container()
    
    # Сортування повідомлень за часом
    messages.sort(key=lambda x: x["timestamp"])
    
    with chat_container:
        st.markdown("<div style='height: 400px; overflow-y: auto; padding: 10px; border: 1px solid #ccc; border-radius: 10px;'>", unsafe_allow_html=True)
        
        # Відображення повідомлень
        for msg in messages:
            is_from_me = msg["from_user_id"] == st.session_state.user_id
            
            col1, col2 = st.columns([1, 5])
            
            with col1:
                st.markdown(f"<p style='text-align: {'right' if is_from_me else 'left'};'>{'Ви' if is_from_me else '👤'}</p>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="{'chat-message-me' if is_from_me else 'chat-message-other'}">
                    <p>{msg['message']}</p>
                    <p style="font-size: 0.8em; text-align: right; opacity: 0.7;">{msg['timestamp']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Форма для надсилання нового повідомлення
    with st.form(key="chat_form"):
        st.markdown("<h3>Надіслати повідомлення</h3>", unsafe_allow_html=True)
        
        message = st.text_area("💬 Текст повідомлення", height=100)
        
        submit_button = st.form_submit_button(label="📤 Надіслати")
        
        if submit_button:
            if message:
                with st.spinner("Надсилання повідомлення..."):
                    if st.session_state.role == "reader":
                        # Для читача надсилаємо повідомлення першому бібліотекарю
                        response, status = send_message(
                            st.session_state.user_id, 1, message)  # Припускаємо, що ID 1 - бібліотекар
                    else:
                        # Для бібліотекаря надсилаємо повідомлення вибраному користувачу
                        response, status = send_message(
                            st.session_state.user_id, to_user_id, message)
                
                if status == 201:
                    st.success("✅ Повідомлення надіслано!")
                    st.rerun()
                else:
                    st.error("❌ " + response["message"])
            else:
                st.warning("⚠️ Будь ласка, введіть повідомлення")

# Сторінка запитів на книги (для бібліотекаря)
def book_requests_page():
    if st.session_state.role != "librarian":
        st.error("❌ У вас немає прав для доступу до цієї сторінки")
        if st.button("↩️ Повернутися до каталогу"):
            navigate_to('catalog')
            st.rerun()
        return
    
    st.markdown("<h1>Запити на книги</h1>", unsafe_allow_html=True)
    
    # Отримання запитів на книги з API
    with st.spinner("Завантаження запитів..."):
        # Додаємо функцію для отримання запитів
        response = requests.get(f"{API_URL}/book_requests")
        if response.status_code == 200:
            requests_data = response.json().get("requests", [])
        else:
            requests_data = []
            st.error("❌ Помилка при отриманні запитів")
    
    # Відображення запитів
    if not requests_data:
        st.info("📭 Немає запитів на розгляд")
    else:
        for i, req in enumerate(requests_data):
            with st.container():
                # Різний колір для різних статусів
                if req['status'] == 'pending':
                    bg_color = "#FFF3CD"  # світло-жовтий для очікування
                    status_text = "⏳ Очікує розгляду"
                elif req['status'] == 'approved':
                    bg_color = "#D4EDDA"  # світло-зелений для схвалених
                    status_text = "✅ Схвалено"
                else:
                    bg_color = "#F8D7DA"  # світло-червоний для відхилених
                    status_text = "❌ Відхилено"
                
                st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 15px; 
                            border-radius: 8px; margin-bottom: 15px;">
                    <p><strong>Користувач ID:</strong> {req['user_id']}</p>
                    <p><strong>Книга ID:</strong> {req['book_id']}</p>
                    <p><strong>Статус:</strong> {status_text}</p>
                    <p><strong>Дата запиту:</strong> {req['request_date']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if req['status'] == 'pending':
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Схвалити", key=f"approve_{req['id']}"):
                            with st.spinner("Оновлення статусу..."):
                                response, status = update_book_request(req['id'], "approved")
                            if status == 200:
                                st.success("✅ Запит схвалено!")
                                st.rerun()
                            else:
                                st.error("❌ " + response["message"])
                    
                    with col2:
                        if st.button("❌ Відхилити", key=f"reject_{req['id']}"):
                            with st.spinner("Оновлення статусу..."):
                                response, status = update_book_request(req['id'], "rejected")
                            if status == 200:
                                st.success("✅ Запит відхилено!")
                                st.rerun()
                            else:
                                st.error("❌ " + response["message"])
    
    st.markdown("<div class='margin-top'></div>", unsafe_allow_html=True)
    if st.button("↩️ Повернутися до каталогу"):
        navigate_to('catalog')
        st.rerun()

# Відображення бічної панелі
def show_sidebar():
    with st.sidebar:
        st.markdown("<h1 style='text-align: center;'>📚 Бібліотека</h1>", unsafe_allow_html=True)
        
        if st.session_state.logged_in:
            st.markdown(f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <div class='avatar' style='width: 80px; height: 80px; margin: 0 auto; background-color: {PRIMARY_COLOR}; color: white; 
                        display: flex; align-items: center; justify-content: center; font-size: 24px;'>
                    {st.session_state.username[0].upper()}
                </div>
                <p style='margin-top: 10px; font-weight: bold;'>Вітаємо, {st.session_state.username}!</p>
                <p>Роль: {'📖 Читач' if st.session_state.role == 'reader' else '👨‍💼 Бібліотекар'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h3>Навігація</h3>", unsafe_allow_html=True)
            
            if st.button("📚 Каталог книг", key="nav_catalog"):
                navigate_to('catalog')
                st.rerun()
            
            if st.button("💬 Чат", key="nav_chat"):
                navigate_to('chat')
                st.rerun()
            
            if st.session_state.role == "librarian":
                if st.button("📋 Запити на книги", key="nav_requests"):
                    navigate_to('book_requests')
                    st.rerun()
            
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            if st.button("🚪 Вийти", key="logout"):
                logout()
                st.rerun()
        else:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background-color: #f0f0f0; border-radius: 10px;'>
                <p>Будь ласка, увійдіть або зареєструйтеся, щоб почати користуватися бібліотечною системою</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Додаємо інформацію про систему внизу сайдбару
        st.markdown("<div style='margin-top: 50px; opacity: 0.7;'>", unsafe_allow_html=True)
        st.markdown("**Інформація про систему**")
        st.markdown("Версія: 1.0.0")
        st.markdown("📧 Підтримка: library.support@example.com")
        st.markdown("</div>", unsafe_allow_html=True)

# Головна функція
def main():
    show_sidebar()
    
    if not st.session_state.logged_in:
        auth_page()
    else:
        if st.session_state.page == 'login':
            auth_page()
        elif st.session_state.page == 'catalog':
            catalog_page()
        elif st.session_state.page == 'book_details':
            book_details_page()
        elif st.session_state.page == 'add_book':
            add_book_page()
        elif st.session_state.page == 'chat':
            chat_page()
        elif st.session_state.page == 'book_requests':
            book_requests_page()

if __name__ == "__main__":
    main()
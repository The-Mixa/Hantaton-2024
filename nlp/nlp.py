import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import faiss
from sklearn.preprocessing import normalize
import requests
import json
from datetime import datetime, timedelta

# Словарь для хранения истории взаимодействий
user_history = {}

# Время хранения сообщений в истории
HISTORY_TIMEOUT = timedelta(minutes=15)


def clean_old_user_histories():
    """Удаление пользователей, которые не были активны более HISTORY_TIMEOUT."""
    current_time = datetime.now()

    inactive_users = [
        user_id for user_id, data in user_history.items()
        if current_time - data['last_active'] > HISTORY_TIMEOUT
    ]
    for user_id in inactive_users:
        del user_history[user_id]


def load_knowledge_base(file_path):
    """Загрузка базы знаний из Excel-файла."""
    data = pd.read_excel(file_path, names=['category', 'comment', 'type'])  # Ожидается таблица с колонками: 'category', 'comment'
    return data


def train_tfidf_classifier(data):
    """Обучение TF-IDF модели и подготовка классификатора."""
    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(data["comment"]).toarray()  # Преобразуем в массив NumPy
    
    # Нормализация L2
    tfidf_matrix = normalize(tfidf_matrix, axis=1)  # Нормализуем по строкам
    
    # Создание FAISS индекса для поиска
    index = faiss.IndexFlatL2(tfidf_matrix.shape[1])
    index.add(tfidf_matrix.astype('float32'))  # Убедитесь, что данные имеют тип float32
    
    return vectorizer, index


def find_category_by_keywords(question, data):
    """Определение категории на основе ключевых слов в вопросе."""
    keywords = question.lower().split()  # Разбиваем вопрос на ключевые слова
    for idx, row in data.iterrows():
        if any(keyword in row['comment'].lower() for keyword in keywords):
            return row['category']
    return None  # Если категория не найдена


def llama_request(prompt, user_messages=None):
    """Отправка запроса к LLM и получение ответа."""
    # URL вашего сервера
    url = 'http://localhost:11434/api/chat'

    # Формируем историю сообщений
    messages = user_messages or []
    messages.append({
        "role": "user",
        "content": prompt
    })

    payload = {
        "model": "llama3.1:8b",
        "messages": messages,
        "stream": False,
        "max_token": 300
    }

    # Отправка POST-запроса
    response = requests.post(
        url,
        data=json.dumps(payload)
    )
    
    return response.json()['message']['content']


def process_user_query(user_id, question, vectorizer, index, data):
    """Обработка запроса пользователя: поиск категории и генерация ответа."""
    clean_old_user_histories()  # Очистка устаревшей истории

    # Преобразуем вопрос пользователя в вектор через TF-IDF
    query_vector = vectorizer.transform([question]).toarray().astype('float32')  # Убедитесь, что тип float32
    
    faiss.normalize_L2(query_vector)

    _, indices = index.search(query_vector, k=1)
    closest_idx = indices[0][0]

    matched_row = data.iloc[closest_idx]
    category = matched_row["category"]
    knowledge = matched_row["comment"]


    # Получение истории сообщений пользователя за последние 15 минут
    user_data = user_history.get(user_id, {"messages": [], "last_active": datetime.now()})
    user_messages = user_data["messages"]


    prompt = (
        f"Вопрос: {question}\nКатегория: {category}\n\n"
        f"Информация по тому как отвечать: {knowledge}\n\n"
        "Пожалуйста, ответь на вопрос, основываясь на данной категории и предоставленной информации по ответу. Не бойся отвечать как думаешь будучи не полностью уверенным в ответе. Твои ответы должны быть полезными\n\n"
        "Если недостаточно данных, сообщи об этом."
    )

    answer = llama_request(prompt, user_messages=user_messages)
    
    user_messages.append({"role": "user", "content": prompt})
    user_messages.append({"role": "assistant", "content": answer})

    user_history[user_id] = {
        "messages": user_messages[-10:],
        "last_active": datetime.now()
    }

    return category, answer



async def get_answer(tgid, question):
    file_path = "nlp/hanthathon_changed.xlsx" 
    knowledge_base = load_knowledge_base(file_path)
    tfidf_vectorizer, faiss_index = train_tfidf_classifier(knowledge_base)
    
    category, response = process_user_query(tgid, question, tfidf_vectorizer, faiss_index, knowledge_base)
    
    return category, response
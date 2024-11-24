# nlp.py

def get_answer(question: str) -> str:
    # Логика для обработки вопроса и возвращения ответа
    if "погода" in question.lower():
        return "Сегодня будет солнечно!"
    elif "где" in question.lower():
        return "В Караганде"
    else:
        return "Извините, я тупой и не понимаю ваш вопрос."
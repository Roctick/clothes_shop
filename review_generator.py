import requests
import json
import logging
import random

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = "sk-1b921002b859441d92891efca15b8ca6"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

def generate_review(address: str, direction: str) -> str:
    """Генерирует отзыв с помощью DeepSeek AI"""
    try:
        prompt = (
            f"Напиши реалистичный отзыв от лица мужчины о {direction} по адресу {address}. "
            f"Требования:\n"
            f"1. Начни с глагола прошедшего времени ('Зашёл', 'Купил') или прилагательного ('Отличный', 'Прекрасный')\n"
            f"2. Объём 30-50 слов, разговорный стиль с мелкими неидеальностями"
            f"3. Употреби адрес '{address}' и направление '{direction}' естественно внутри текста\n"
            f"4. Добавь бытовую деталь (например: 'устал после работы', 'торопился на встречу')\n"
            f"5. Избегай шаблонных фраз вроде 'высокий уровень сервиса'\n"
            f"6. Без форматирования, кавычек и спецсимволов\n"
            f"Пример структуры: 'Забежал вчера в {direction} на {address}. Реально выручили, когда срочно нужен был...'"
        )
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system", 
                    "content": "Ты русскоязычный клиент, который пишет формальный отзыв в стиле разговорной речи."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 1.2,  # Увеличено для вариативности
            "max_tokens": 100,    # Жёсткое ограничение длины
            "top_p": 0.95
        }
        
        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        review = result["choices"][0]["message"]["content"].strip()
        
        # Фикс длины (удаляем последнее неоконченное предложение)
        if len(review.split()) > 50:
            review = " ".join(review.split()[:50])
            if review[-1] not in ".!?":
                review = review.rsplit('.', 1)[0] + '.' 
                
        logger.info(f"Сгенерирован отзыв для {direction} по адресу {address}")
        return review
        
    except Exception as e:
        logger.error(f"Ошибка генерации отзыва: {str(e)}")
        return f"Зашёл в {direction} на {address}. Остался доволен! Всё быстро, без лишних вопросов. Ребята знают своё дело."

# Тестирование
if __name__ == "__main__":
    test_review = generate_review("ул. Пушкина, 15", "магазин электроники")
    print("Тестовый отзыв:")
    print(test_review)
    print(f"Слов: {len(test_review.split())}")
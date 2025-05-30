import requests
import json
import logging

# Настройка логирования
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
            f"Напиши положительный отзыв от мужского лица про опыт покупки в {direction} по адресу {address}. "
            "Объем до 50 слов, без форматирования. Сделай отзыв естественным, не похожим на накрученный. "
            "Каждый раз используй разную структуру."
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
                    "content": "Ты профессиональный копирайтер, специализирующийся на создании отзывов для бизнеса."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        review = result["choices"][0]["message"]["content"].strip()
        
        logger.info(f"Сгенерирован отзыв для {direction} по адресу {address}")
        return review
        
    except Exception as e:
        logger.error(f"Ошибка генерации отзыва: {str(e)}")
        return f"Отличный сервис {direction} по адресу {address}! Быстрое обслуживание и приветливый персонал."

# Для проверки работы функции
if __name__ == "__main__":
    test_review = generate_review("ул. Пушкина, 15", "магазин электроники")
    print("Тестовый отзыв:")
    print(test_review)
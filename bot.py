import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import aiohttp

# Загрузка переменных окружения
load_dotenv()

# Настройка логгера
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DeepseekHandler:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def get_response(self, user_message: str) -> str:
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    json=payload,
                    headers=self.headers,
                    timeout=30
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data['choices'][0]['message']['content']
        
        except Exception as e:
            logger.error(f"Deepseek API Error: {e}")
            return "Извините, произошла ошибка обработки запроса."

async def start(update: Update, context):
    await update.message.reply_text("Привет! Я простой бот, подключенный к Deepseek. Задайте вопрос:")

async def handle_message(update: Update, context):
    deepseek = DeepseekHandler(os.getenv("DEEPSEEK_API_KEY"))
    user_input = update.message.text
    
    await update.message.chat.send_action(action="typing")
    response = await deepseek.get_response(user_input)
    
    await update.message.reply_text(response[:4000])  # Обрезка для Telegram

def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()

import psutil
import telegram
from telegram.ext import Updater

# Telegram bot token
TOKEN = '1439670844:AAFejYbp5TSMcuWMW_TxUDSKiho1Ht7gc7w'

# Chat ID for receiving messages
CHAT_ID = '66395090'

# Create a Telegram bot object
bot = telegram.Bot(token=TOKEN)

# Create an Updater object to handle incoming updates
updater = Updater(token=TOKEN, use_context=True)

# Get the current system CPU usage
cpu_usage = psutil.cpu_percent()

# Get the current system memory usage
memory_usage = psutil.virtual_memory().percent

# Get the current system disk usage
disk_usage = psutil.disk_usage('/').percent

# Create a message with system information
message = f"CPU usage: {cpu_usage}%\nMemory usage: {memory_usage}%\nDisk usage: {disk_usage}%"

# Send the message to the specified chat ID
bot.send_message(chat_id=CHAT_ID, text=message)

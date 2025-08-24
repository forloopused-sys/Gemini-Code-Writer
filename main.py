import logging
import os
import asyncio
from functools import wraps

import google.generativeai as genai
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from supabase import create_client, Client

# --- Configuration ---
# Replace with your actual Telegram bot token.
# You can get this from BotFather on Telegram.
TELEGRAM_BOT_TOKEN = "8186162237:AAEK6QD6XKt3y5swaYjw2T_lCRpY8g8J4SM" 

# Gemini API Key (provided by the user)
GEMINI_API_KEY = "AIzaSyDLLUpqxNecGINHCz43Bi7ma1JUP9NmNKE"

# Supabase Configuration (provided by the user)
SUPABASE_URL = "https://wlnwmsoxvqhbdktxidki.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indsbndtc294dnFoYmRrdHhpZGtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYwNTI3MTgsImV4cCI6MjA3MTYyODcxOH0.iJXb6iFXp65U1yq9rUBZNdys6Xqz0LDx6nVIQdJv5lQ"

# Supabase table name for storing interactions
SUPABASE_TABLE_NAME = "bot_interactions"

# --- Setup Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Initialize Gemini and Supabase ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro') # Using 'gemini-pro' for text generation
    logger.info("Gemini model initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing Gemini: {e}")
    gemini_model = None # Set to None if initialization fails

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    logger.info("Supabase client initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing Supabase: {e}")
    supabase = None # Set to None if initialization fails

# --- Utility Functions ---

def retry_async(max_retries=3, delay=1):
    """Decorator for retrying async functions with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {i+1}/{max_retries} failed for {func.__name__}: {e}")
                    if i < max_retries - 1:
                        await asyncio.sleep(delay * (2 ** i)) # Exponential backoff
            raise
        return wrapper
    return decorator

@retry_async(max_retries=3)
async def save_interaction_to_supabase(user_id: int, username: str, user_code: str, bot_response: str):
    """Saves user interaction data to Supabase."""
    if not supabase:
        logger.error("Supabase client not initialized. Cannot save interaction.")
        return

    try:
        data = {
            "user_id": str(user_id), # Store as string for flexibility
            "username": username,
            "user_code": user_code,
            "bot_response": bot_response
        }
        response = supabase.table(SUPABASE_TABLE_NAME).insert(data).execute()
        if response.data:
            logger.info(f"Interaction saved for user {user_id}")
        else:
            logger.error(f"Failed to save interaction for user {user_id}: {response.error}")
    except Exception as e:
        logger.error(f"Error saving interaction to Supabase: {e}")

@retry_async(max_retries=3)
async def get_gemini_explanation(code: str) -> str:
    """Gets code explanation or fixes from Gemini API."""
    if not gemini_model:
        return "Sorry, the AI model is not available at the moment. Please try again later."

    prompt = (
        "You are a helpful coding assistant. A user has provided the following code snippet.\n"
        "Please identify any potential errors, suggest fixes, or explain the code in detail.\n"
        "Keep your explanation concise and to the point.\n\n"
        "```\n"
        f"{code}\n"
        "```"
    )
    try:
        response = await asyncio.to_thread(gemini_model.generate_content, prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating content with Gemini: {e}")
        return "I apologize, but I encountered an error while trying to process your code. Please try again."

# --- Telegram Bot Handlers ---

async def start_command(update: Update, context: Application) -> None:
    """Sends a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! 👋\n"
        "I'm your Coding Helper Bot 👨‍💻. Send me any code snippet, and I'll try to explain errors or suggest fixes!",
        reply_markup=ForceReply(selective=True),
    )
    logger.info(f"User {user.id} started the bot.")

async def help_command(update: Update, context: Application) -> None:
    """Sends a message when the command /help is issued."""
    await update.message.reply_text(
        "Just send me your code! I'll do my best to help you understand it or find issues. "
        "I can work with various programming languages."
    )
    logger.info(f"User {update.effective_user.id} requested help.")

async def handle_code_message(update: Update, context: Application) -> None:
    """Handles incoming text messages (assumed to be code) and sends them to Gemini."""
    user = update.effective_user
    user_code = update.message.text
    chat_id = update.effective_chat.id

    logger.info(f"User {user.id} ({user.username}) sent code.")
    
    # Send a typing indicator and a loading message
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    loading_message = await update.message.reply_text("Analyzing your code... this might take a moment. 🚀")

    try:
        bot_response = await get_gemini_explanation(user_code)
        await update.message.reply_text(bot_response)
        logger.info(f"Bot responded to user {user.id} with Gemini explanation.")

        # Save interaction to Supabase in the background
        await save_interaction_to_supabase(user.id, user.username, user_code, bot_response)

    except Exception as e:
        logger.error(f"Error handling code message for user {user.id}: {e}")
        await update.message.reply_text(
            "Oops! Something went wrong while processing your code. Please try again or check the logs."
        )
    finally:
        # Delete the loading message
        await loading_message.delete()


def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        logger.error("Telegram bot token not set. Please replace 'YOUR_TELEGRAM_BOT_TOKEN' in the script.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # On non-command messages - handle the code
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code_message))

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot started successfully. Press Ctrl-C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

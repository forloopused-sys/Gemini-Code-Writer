# Gemini-Code-Writer

Coding Helper Bot 👨‍💻
A Telegram bot that helps developers by explaining code, identifying errors, and suggesting fixes using the Gemini AI, with all interactions logged in a Supabase database.

✨ Features
Code Explanation: Send any code snippet, and the bot will provide a detailed explanation.

Error Identification: Helps pinpoint errors in your code.

Fix Suggestions: Offers potential solutions or improvements for your code.

Interaction Logging: All user interactions and bot responses are saved to a Supabase database for tracking and analysis.

🛠️ Prerequisites
Before you begin, ensure you have the following:

Python 3.8+ installed on your system.

A Telegram Bot Token: Obtain this by talking to @BotFather on Telegram.

A Google Gemini API Key: Your provided key (AIzaSyDLLUpqxNecGINHCz43Bi7ma1JUP9NmNKE).

A Supabase Project: With your provided URL (https://wlnwmsoxvqhbdktxidki.supabase.co) and Anon Key (eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indsbndtc294dnFoYmRrdHhpZGtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYwNTI3MTgsImV4cCI6MjA3MTYyODcxOH0.iJXb6iFXp65U1yq9rUBZNdys6Xqz0LDx6nVIQdJv5lQ).

🚀 Installation
Follow these steps to get your bot up and running:

Clone the repository (or save the code):
If you have a Git repository, clone it:

git clone <your-repository-url>
cd <your-repository-name>

Otherwise, save the bot's Python code (e.g., bot.py) and the requirements.txt file in a directory.

Create a virtual environment (recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:
Use the provided requirements.txt to install all necessary libraries:

pip install -r requirements.txt

The requirements.txt contains:

python-telegram-bot==21.2
google-generativeai==0.7.1
supabase==2.4.0

Configure Environment Variables/Bot Code:
Open your bot's Python file (bot.py or similar) and update the TELEGRAM_BOT_TOKEN variable with your actual token. The Gemini and Supabase keys are already provided in the code.

# Inside your bot.py file
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" # <-- REPLACE THIS
GEMINI_API_KEY = "YOUR_API_KEY"
SUPABASE_URL = "YOUR_URL"
SUPABASE_ANON_KEY = "YOUR_API_KEY

🗄️ Supabase Table Setup
You need to create a table in your Supabase project to store bot interactions.

Go to your Supabase project dashboard.

Navigate to the Table Editor section.

Click "New Table" and configure it as follows:

Name: bot_interactions

Columns:

id: uuid (Primary Key, Default Value: gen_random_uuid())

created_at: timestamp with time zone (Default Value: now())

user_id: text

username: text (Allow Nullable)

user_code: text

bot_response: text

▶️ Running the Bot
Once all prerequisites and configurations are set, you can run the bot:

python bot.py  # Or whatever you named your bot's Python file

The bot will start polling for updates from Telegram.

💬 Usage
Start a chat with your bot on Telegram.

Send the /start command to greet the bot.

Send any code snippet (e.g., Python, JavaScript, Java, etc.) directly in the chat.

The bot will process the code using Gemini AI and reply with an explanation, error analysis, or suggested fix.

All your interactions will be logged in your Supabase bot_interactions table.

🤝 Contributing
(Optional section: Add information on how others can contribute if this is an open-source project.)

📄 License
(Optional section: Specify the license under which your project is released.)

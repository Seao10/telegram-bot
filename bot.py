import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your tokens
CLICKUP_API_URL = "https://flask-hello-world-xi-ashen.vercel.app/clickup"  # e.g., "https://your-app.vercel.app/clickup"
TELEGRAM_TOKEN = "7689450336:AAFDb3T3GA1NKoYhSyIPYr_HXjfIMtLhtJQ"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Hi! I'm your ClickUp assistant. You can:\n\n"
        "1. Create a task: 'create a task called meeting prep'\n"
        "2. Get tasks: 'show my tasks'\n"
        "3. Update task: 'mark task XYZ as complete'\n\n"
        "Just type your request naturally!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Here's how to use me:\n\n"
        "🎯 Create Task: 'create a task called [name] with description [desc]'\n"
        "📋 View Tasks: 'show my tasks' or 'get my tasks'\n"
        "✏️ Update Task: 'update task [id] status to [status]'\n\n"
        "Examples:\n"
        "- create a task called Weekly Report due tomorrow\n"
        "- show my pending tasks\n"
        "- mark task 123 as complete"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the user message."""
    try:
        # Send the "typing" action
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
        
        # Get the user's message
        user_input = update.message.text
        
        # Make request to your API
        response = requests.post(
            CLICKUP_API_URL,
            json={"user_input": user_input}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle different types of responses
            if "tasks" in data:
                # Format tasks list
                tasks_text = "📋 Here are your tasks:\n\n"
                for task in data["tasks"]:
                    tasks_text += f"🔹 {task['name']}\n"
                    tasks_text += f"   ID: {task['id']}\n"
                    tasks_text += f"   Status: {task['status']}\n\n"
                await update.message.reply_text(tasks_text)
            
            elif "message" in data:
                await update.message.reply_text(f"✅ {data['message']}")
            
            else:
                await update.message.reply_text(str(data))
        
        else:
            error_message = response.json().get('error', 'Unknown error occurred')
            await update.message.reply_text(f"❌ Error: {error_message}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await update.message.reply_text("❌ Sorry, something went wrong. Please try again later.")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()

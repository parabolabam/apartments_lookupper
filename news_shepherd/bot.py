from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
from .apartment import parse_apartment_message
from .ai_processor import ApartmentAIProcessor
import logging

load_dotenv()

# Telegram API credentials
API_ID = int(os.getenv("API_ID") or "")
API_HASH = os.getenv("API_HASH") or ""
BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
MESSAGE_LIMIT = int(os.getenv("MESSAGE_LIMIT")) or 100
CHANNEL_NAME = "@kvartiry_v_tbilisi"

if API_ID is None or API_HASH == "" or CHANNEL_NAME == "" or BOT_TOKEN == "" or BOT_TOKEN == "":
    raise ValueError(
        "API_ID, API_HASH, BOT_TOKEN, and CHANNEL_NAME must be set in the environment."
    )

# Initialize Telethon client
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Initialize AI processor

logger = logging.getLogger(__name__)

async def fetch_messages(user_preferences, ai_processor):
    """Fetch and analyze messages from the channel based on user preferences."""
    # Create user criteria using AI
    user_criteria = await ai_processor.create_user_criteria(user_preferences)
    
    results = []
    
    async for message in bot.iter_messages(CHANNEL_NAME, limit=MESSAGE_LIMIT):
        try:
            # Skip messages without text
            if not message.text:
                continue
                
            # Parse the apartment listing
            parsed_data = parse_apartment_message(message.text)
            if not parsed_data:
                continue
                
            # Analyze the listing against user criteria
            ai_analysis = await ai_processor.analyze_listing(
                message.text,
                user_criteria
            )
            
            # If the listing matches criteria, add to results
            if ai_analysis.get('matches_criteria'):
                results.append({
                    "message_id": message.id,
                    "text": message.text,
                    "parsed_data": parsed_data,
                    "ai_analysis": ai_analysis,
                    "link": f"https://t.me/{CHANNEL_NAME.lstrip('@')}/{message.id}"
                })
                
        except Exception as e:
            logger.error(f"Error processing message {message.id}: {str(e)}")
            continue
            
    return results

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        "Welcome to Apartment Search! 🏠\n\n"
        "Please describe what kind of apartment you're looking for using the /search command.\n\n"
        "Example: `/search 2-bedroom apartment in Vake, budget $800-1000, must have parking`"
    )

@bot.on(events.NewMessage(pattern='/search'))
async def search(event):
    # Get the search criteria (everything after /search)
    user_preferences = event.text.replace('/search', '').strip()
    
    if not user_preferences:
        await event.respond(
            "Please provide your search criteria after the /search command.\n"
            "Example: `/search 2-bedroom apartment in Vake, budget $800-1000`"
        )
        return

    await event.respond("🔍 Searching for apartments matching your criteria...")
    
    try:
        ai_processor = ApartmentAIProcessor()
        results = await fetch_messages(user_preferences, ai_processor)
        
        if not results:
            await event.respond("😔 No apartments found matching your criteria. Try adjusting your search parameters! 🔄")
            return
            
        await event.respond(f"Found {len(results)} apartments:")
        
        # Send each result as a separate message
        for result in results[:10]:  # Limit to first 10 results
            parsed_data = result["parsed_data"]
            ai_analysis = result["ai_analysis"]
            
            message = (
                f"🏠 *Apartment Details:*\n"
                f"Price: {parsed_data.get('price', 'N/A')}\n"
                f"Location: {parsed_data.get('location', 'N/A')}\n"
                f"Rooms: {parsed_data.get('rooms', 'N/A')}\n\n"
                f"*AI Analysis:*\n"
                f"Matches Criteria: {'✅' if ai_analysis.get('matches_criteria') else '❌'}\n"
                f"Match Explanation: {ai_analysis.get('explanation', 'N/A')}"
            )
            
            await event.respond(message, parse_mode='markdown')
            
    except Exception as e:
        await event.respond(f"An error occurred: {str(e)}")

# Start the bot
def main():
    print("Bot started...")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
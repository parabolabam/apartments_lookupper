from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
from .apartment import parse_apartment_message
from .apartment_ai_processor import ApartmentAIProcessor
import logging
from .constants import CHANNELS

load_dotenv()

# Telegram API credentials
API_ID = int(os.getenv("API_ID") or "")
API_HASH = os.getenv("API_HASH") or ""
BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
MESSAGE_LIMIT = int(os.getenv("MESSAGE_LIMIT") or 100)

if API_ID is None or API_HASH == "" or BOT_TOKEN == "":
    raise ValueError(
        "API_ID, API_HASH, BOT_TOKEN, and CHANNEL_NAME must be set in the environment."
    )

# Initialize Telethon client
client = TelegramClient("anon", API_ID, API_HASH)

bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Initialize AI processor

logger = logging.getLogger(__name__)


async def merge_iterators(*iterators):
    for it in iterators:
        async for item in it:
            yield item


async def fetch_messages():
    """Fetch and analyze messages from the channel based on user preferences."""
    # Create user criteria using AI

    results = []

    await client.connect()

    # Flatten the list of iterators
    messages = merge_iterators(
        *(client.iter_messages(channel, limit=MESSAGE_LIMIT) for channel in CHANNELS)
    )
    async for message in messages:
        try:
            # Skip messages without text
            if not message.text:
                continue

            # Parse the apartment listing
            parsed_data = parse_apartment_message(message)
            if not parsed_data:
                continue

            # If the listing matches criteria, add to results
            results.append(parsed_data)

        except Exception as e:
            logger.error(f"Error processing message {message.id}: {str(e)}")
            continue

    return results


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(
        "Welcome to Apartment Search! 🏠\n\n"
        "Please describe what kind of apartment you're looking for using the /search command.\n\n"
        "Example: `/search 2-bedroom apartment in Vake, budget $800-1000, must have parking`"
    )


@bot.on(events.NewMessage(pattern="/search"))
async def search(event):
    # Get the search criteria (everything after /search)
    user_preferences = event.text.replace("/search", "").strip()

    if not user_preferences:
        await event.respond(
            "Please provide your search criteria after the /search command.\n"
            "Example: `/search 2-bedroom apartment in Vake, budget $800-1000`"
        )
        return

    await event.respond("🔍 Searching for apartments matching your criteria...")

    try:
        ai_processor = ApartmentAIProcessor()
        # Analyze the listing against user criteria
        user_criteria = await ai_processor.create_user_criteria(user_preferences)

        results = await fetch_messages()
        ai_analysis = await ai_processor.analyze_listing_batch(results, user_criteria)

        matched_apartments = [
            result for result in ai_analysis["results"] if result["matches_criteria"]
        ]

        if not matched_apartments:
            await event.respond(
                "😔 No apartments found matching your criteria. Try adjusting your search parameters! 🔄"
            )
            return

        # Send each result as a separate message
        for result in matched_apartments:  # Limit to first 10 results

            location = (
                result["extracted_info"].get("maps_link")
                or result["extracted_info"].get("maps_location_link")
                or result["extracted_info"].get("location_link")
                or "N/A"
            )
            message = (
                f"Found {len(matched_apartments)} apartments matching your criteria:\n\n"
                f"🏠 *Apartment Details:*\n"
                f"Price: {result['extracted_info']['price'] if 'price' in result['extracted_info'] else 'N/A'}\n"
                f"Original Link: {result['extracted_info']['telegram_link'] if 'telegram_link' in result['extracted_info'] else 'N/A'}\n"
                f"Location: {location}\n"
                f"Rooms: {result['extracted_info']['rooms'] if 'rooms' in result['extracted_info'] else 'N/A'}\n"
                f"\n*AI Analysis:*\n"
                f"Match Explanation: {result['thorough_explanation'] or 'N/A'}"
            )

            await event.respond(message, parse_mode="markdown")

    except Exception as e:
        await event.respond(f"An error occurred: {str(e)}")

# Start the bot
def main():
    print("Bot started...")
    bot.run_until_disconnected()

if __name__ == "__main__":
    main()

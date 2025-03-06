from pyrogram import Client, filters
import re

# Replace these with your credentials
api_id = "12380656"
api_hash = "d927c13beaaf5110f25c505b7c071273"
bot_token = "7786173774:AAG-6K0llfPrW78CFvwFPYr0AZnjxFFOXI0"

app = Client("cleaner_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def format_links(text):
    # Remove the pin emoji from the text
    text = text.replace("📌", "")

    # Initialize categories in the required order
    grouped_links = {
        "2022": [],
        "2021": [],
        "2020": [],
        "2022 Low": [],
        "2021 Low": [],
        "2020 Low": [],
        "Others": []
    }

    # Extract and categorize links
    for line in text.split("\n"):
        match = re.search(r"(\d{4})\s*(low)?\s*→\s*(https://t\.me/\+\S+)", line, re.IGNORECASE)
        if match:
            year, low, link = match.groups()
            category = f"{year} Low" if low else year
            if category in grouped_links:
                grouped_links[category].append(link)
            else:
                grouped_links["Others"].append(link)
        else:
            # If no structured match, check for an orphaned link
            link_match = re.search(r"(https://t\.me/\+\S+)", line)
            if link_match:
                grouped_links["Others"].append(link_match.group(1))

    # Build the response message following the required order
    response = ""
    order = ["2022", "2021", "2020", "2022 Low", "2021 Low", "2020 Low", "Others"]
    total_links = 0

    for category in order:
        if grouped_links[category]:
            response += f"{category}\n" + "\n".join(grouped_links[category]) + "\n\n"
            total_links += len(grouped_links[category])

    # Add total count of links at the end
    response += f"Total Links: {total_links}"

    return response.strip()

# /clean command: Reply to a message containing the links with the cleaned output
@app.on_message(filters.command("cl"))
async def clean_links(_, message):
    if not message.reply_to_message:
        await message.reply("Please reply to a message containing group links.")
        return

    cleaned_text = format_links(message.reply_to_message.text)
    if cleaned_text:
        await message.reply(cleaned_text)
    else:
        await message.reply("No Telegram group links found.")

# (Optional) Auto-cleaning: Automatically detect, format, and replace messages that contain group links
AUTO_CLEAN = False  # Change to True to enable auto-cleaning
if AUTO_CLEAN:
    @app.on_message(filters.text)
    async def auto_clean(_, message):
        cleaned_text = format_links(message.text)
        if cleaned_text:
            await message.delete()
            await message.reply(cleaned_text)

app.run()
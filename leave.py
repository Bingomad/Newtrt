import json
from telethon import TelegramClient, events
from telethon.tl.functions.channels import LeaveChannelRequest

# 🔹 Replace with your actual credentials
API_ID = 12380656
API_HASH = "d927c13beaaf5110f25c505b7c071273"
BOT_TOKEN = "7786173774:AAG-6K0llfPrW78CFvwFPYr0AZnjxFFOXI0"

# Use a session file for authentication
bot = TelegramClient("lbot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 🔹 File to store joined groups
GROUPS_FILE = "groups.json"


def load_groups():
    """Load stored groups from a file."""
    try:
        with open(GROUPS_FILE, "r") as f:
            return set(json.load(f))  # Convert list to set for fast lookups
    except FileNotFoundError:
        return set()


def save_groups():
    """Save groups to a file."""
    with open(GROUPS_FILE, "w") as f:
        json.dump(list(joined_groups), f)  # Convert set to list for JSON


# 🔹 Load groups at startup
joined_groups = load_groups()


@bot.on(events.ChatAction)
async def track_groups(event):
    """Track groups where the bot is added or removed."""
    if event.user_added and event.user_id == (await bot.get_me()).id:
        joined_groups.add(event.chat_id)
        save_groups()  # Save when added
        print(f"✅ Bot added to: {event.chat.title}")

    elif event.user_kicked and event.user_id == (await bot.get_me()).id:
        joined_groups.discard(event.chat_id)
        save_groups()  # Save when removed
        print(f"❌ Bot removed from: {event.chat.title}")


@bot.on(events.NewMessage(pattern=r"^/leaveall$"))
async def leave_all(event):
    """Command: /leaveall -> Leaves all stored groups."""
    sender = await event.get_sender()
    if not sender.bot:  # Prevent other bots from using the command
        if not joined_groups:
            await event.reply("⚠ No groups to leave.")
            return

        await event.reply("⏳ Leaving all groups...")

        for chat_id in list(joined_groups):  # Convert to list to avoid modification issues
            try:
                await bot(LeaveChannelRequest(chat_id))
                joined_groups.discard(chat_id)
                save_groups()  # Save changes
                print(f"✅ Left {chat_id}")
            except Exception as e:
                print(f"❌ Failed to leave {chat_id}: {e}")

        await event.reply("✅ Successfully left all groups.")


print("✅ Bot is running... Waiting for commands!")
bot.run_until_disconnected()

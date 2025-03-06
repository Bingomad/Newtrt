import logging
import asyncio
from telethon import TelegramClient, events7786173774
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

# 🔹 API Credentials
API_ID = 12380656
API_HASH = "d927c13beaaf5110f25c505b7c071273"
BOT_TOKEN = ":AAG-6K0llfPrW78CFvwFPYr0AZnjxFFOXI0"

# 🔹 Initialize bot
bot = TelegramClient("mbot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 🔹 Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@bot.on(events.NewMessage(pattern=r"^/banall$"))
async def ban_all(event):
    """Command: /banall -> Bans all non-admins (including bots), skips admins & self."""

    if not event.is_group:
        await event.reply("❌ This command can only be used in a group.")
        return

    chat = event.chat_id
    sender = event.sender_id
    bot_user = await bot.get_me()

    # ✅ Check if the sender is an admin
    try:
        sender_permissions = await bot.get_permissions(chat, sender)
        if not sender_permissions.is_admin:
            await event.reply("⚠️ You must be an **admin** to use this command.")
            return
    except Exception as e:
        await event.reply(f"❌ Error checking your admin status: {e}")
        return

    # ✅ Check if the bot is an admin
    try:
        bot_permissions = await bot.get_permissions(chat, bot_user.id)
        if not bot_permissions.is_admin:
            await event.reply("❌ I need 'Ban Users' permission to execute this command.")
            return
    except Exception:
        await event.reply("❌ Error checking bot admin status.")
        return

    try:
        banned_count = 0
        tasks = []

        async for user in bot.iter_participants(chat):
            # ✅ Skip the bot itself
            if user.id == bot_user.id:
                continue

            # ✅ Check if the user is an admin
            user_permissions = await bot.get_permissions(chat, user.id)
            if user_permissions.is_admin:
                continue  # ❌ Skip other admins

            # ✅ Add the user to the ban task list
            tasks.append(ban_user(chat, user.id))

        results = await asyncio.gather(*tasks)  # ✅ Run all bans in parallel
        banned_count = sum(results)  # ✅ Count only successful bans

        await event.reply(f"✅ Successfully removed {banned_count} members (including bots) from the group.")

    except Exception as e:
        logging.error(f"❌ Error in /banall: {e}")
        await event.reply(f"❌ Error: {str(e)}")


async def ban_user(chat_id, user_id):
    """Ban a user asynchronously and return 1 if successful, 0 if failed."""
    try:
        rights = ChatBannedRights(until_date=None, view_messages=True)
        await bot(EditBannedRequest(chat_id, user_id, rights))
        logging.info(f"✅ Banned user {user_id}")
        return 1  # ✅ Success
    except Exception as e:
        logging.warning(f"❌ Failed to ban {user_id}: {e}")
        return 0  # ❌ Failure


logging.info("✅ Bot is running... Waiting for /banall command!")
bot.run_until_disconnected()

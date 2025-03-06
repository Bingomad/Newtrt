import os
import json
from telethon.sync import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.functions.messages import ExportChatInviteRequest  # ✅ FIXED IMPORT
from telethon.tl.types import ChannelParticipantAdmin

API_ID = 12380656
API_HASH = "d927c13beaaf5110f25c505b7c071273"
BOT_TOKEN = "7786173774:AAG-6K0llfPrW78CFvwFPYr0AZnjxFFOXI0"

bot = TelegramClient("fbot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

GROUPS_FILE = "group_links.json"

if os.path.exists(GROUPS_FILE):
    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        registered_groups = json.load(f)
else:
    registered_groups = {}


@bot.on(events.NewMessage(pattern=r"^/find$"))
async def find_admin_groups(event):
    if not event.is_private:
        await event.reply("❌ Please use this command in my DM.")
        return

    admin_groups = []

    for chat_id in registered_groups.keys():
        try:
            chat_id_int = int(chat_id)  # ✅ Convert string to integer
            participant = await bot(GetParticipantRequest(chat_id_int, "me"))

            if isinstance(participant.participant, ChannelParticipantAdmin):
                group_name = registered_groups[chat_id]["name"]
                group_link = registered_groups[chat_id]["link"]
                admin_groups.append(f"📌 {group_name} → {group_link}")

        except Exception as e:
            print(f"⚠ Error checking {chat_id}: {str(e)}")

    if admin_groups:
        result = "\n".join(admin_groups)
        await event.reply(f"**Your Admin Groups:**\n\n{result}")
    else:
        await event.reply("❌ I'm not an admin in any group.")


@bot.on(events.NewMessage(pattern=r"^/register$"))
async def register_group(event):
    if not event.is_group:
        await event.reply("❌ This command must be used in a group.")
        return

    chat = await event.get_chat()

    if str(chat.id) in registered_groups:
        await event.reply("⚠️ This group is already registered!")
        return

    try:
        invite = await bot(ExportChatInviteRequest(chat.id))  # ✅ Uses correct import
        registered_groups[str(chat.id)] = {"name": chat.title, "link": invite.link}

        with open(GROUPS_FILE, "w", encoding="utf-8") as f:
            json.dump(registered_groups, f, indent=4)

        await event.reply(f"✅ Group '{chat.title}' has been registered!\nLink: {invite.link}")

    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")


print("✅ Bot is running... Waiting for commands!")
bot.run_until_disconnected()

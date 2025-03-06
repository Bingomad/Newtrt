from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes

# Your bot token
BOT_TOKEN = '7786173774:AAG-6K0llfPrW78CFvwFPYr0AZnjxFFOXI0'

async def set_group_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ensure the command is used in a group
    if update.message.chat.type in ("group", "supergroup"):
        # Check if the user is an admin
        user = await context.bot.get_chat_member(update.message.chat_id, update.message.from_user.id)
        if user.status in ["administrator", "creator"]:
            # Extract new group name from the command
            new_name = ' '.join(context.args)
            if new_name:
                try:
                    # Rename the group
                    await context.bot.set_chat_title(update.message.chat_id, new_name)
                    rename_success = True
                except Exception as e:
                    rename_success = False
                    await update.message.reply_text(f"⚠️ Failed to rename the group. Error: {e}")

                try:
                    # Remove the group description
                    await context.bot.set_chat_description(update.message.chat_id, '')
                    desc_success = True
                except Exception as e:
                    if "Chat description is not modified" in str(e):
                        desc_success = True  # Ignore this specific error
                    else:
                        desc_success = False
                        await update.message.reply_text(f"⚠️ Failed to remove the description. Error: {e}")

                # Check if a linked channel exists (before setting permissions)
                try:
                    chat = await context.bot.get_chat(update.message.chat_id)
                    if chat.linked_chat_id:
                        await update.message.reply_text(
                            "⚠️ This group has a linked channel.\n"
                            "🚨 **Bots are not allowed to unlink channels** automatically.\n"
                            "❗ **To unlink it, go to group settings and remove the linked channel manually.**"
                        )
                        linked_channel_found = True
                    else:
                        linked_channel_found = False
                        await update.message.reply_text("ℹ️ No linked channel found for this group.")
                except Exception as e:
                    linked_channel_found = False
                    await update.message.reply_text(f"⚠️ Failed to check for a linked channel. Error: {e}")

                # Open all permissions for members (Only if no linked channel)
                perm_success = False
                if update.message.chat.type == "supergroup" and not linked_channel_found:
                    permissions = ChatPermissions(
                        can_send_messages=True,
                        can_send_other_messages=True,
                        can_send_polls=True,
                        can_add_web_page_previews=True,
                        can_change_info=True,
                        can_invite_users=True,
                        can_pin_messages=True,
                        can_manage_topics=True
                    )
                    try:
                        await context.bot.set_chat_permissions(update.message.chat_id, permissions)
                        perm_success = True
                    except Exception as e:
                        if "Chat_not_modified" in str(e):
                            perm_success = True  # Ignore error if permissions are already set
                        else:
                            await update.message.reply_text(f"⚠️ Failed to update permissions. Error: {e}")

                # Final success message
                final_message = f"✅ Group renamed to: {new_name}\n"
                final_message += "✅ Group description removed (or already empty).\n"

                if not linked_channel_found:
                    if perm_success:
                        final_message += "✅ All permissions have been opened for members.\n"
                else:
                    final_message += "ℹ️ **Group permissions were not changed because a channel is linked.**\n"

                await update.message.reply_text(final_message)
            else:
                await update.message.reply_text("⚠️ Please provide a new name after the command.")
        else:
            await update.message.reply_text("⚠️ You must be an admin to use this command.")
    else:
        await update.message.reply_text("⚠️ This command can only be used in groups.")

def main():
    # Create the bot application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add the command handler
    application.add_handler(CommandHandler("set", set_group_name))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()

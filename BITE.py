import os
import asyncio
import time
from collections import defaultdict
from telethon import TelegramClient, events, functions
from telethon.tl.types import UserStatusOnline

# Configuration (Use environment variables for security)
api_id = '25305140'  # Replace with your API ID
api_hash = '6d19044c96341ccb3da294f878df7659'  # Replace with your API Hash
session_name = 'self_bot_god'  # Session name (must be a valid filename)

# Initialize Telegram Client
client = TelegramClient(session_name, api_id, api_hash)
current_status = "offline"
cooldown = defaultdict(float)  # {user_id: last_reply_time}

# Messages
OFFLINE_MESSAGE = '''
🌀 <b>Automated Response</b> 🌀

┏━━━━━━━━━━━━━━━━┓
┃  ⚡️ <i>Status:</i> <b>OFFLINE</b> ⚡️
┃  🕒 <i>Next Check:</i> <b>30 Mins</b> 🕒
┗━━━━━━━━━━━━━━━━┛

📡 <i>Your message has been queued! 
I'll respond when I return to network.</i> 📡

✨ <code>🔒 Premium Auto-Reply System 🔒</code> ✨
'''

ONLINE_MESSAGE = '''
🌟 <b>CURRENTLY ACTIVE</b> 🌟

⏳ <i>Last Online:</i> <b>JUST NOW</b> ⏳

🌐 <code>Premium Connection • Pro</code> 🌐
'''

@client.on(events.UserUpdate)
async def handle_status_update(event):
    global current_status
    user = await event.get_user()
    
    # Debug print to check the user object
    print(f"User object: {user}")
    
    # Check if user is not None and is a User object
    if user is None or not hasattr(user, 'is_self'):
        print("User is None or not a User object")
        return
    
    # Check if the user is the logged-in user
    if user.is_self:
        # Check if user.status is not None and is a valid status
        if hasattr(user, 'status') and user.status is not None:
            current_status = "online" if isinstance(user.status, UserStatusOnline) else "offline"
            print(f"Status updated: {current_status}")

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply(event):
    sender = await event.get_sender()
    
    # Debug print to check the sender object
    print(f"Sender object: {sender}")
    
    # Check if sender is not None and is a valid user object
    if sender is None or not hasattr(sender, 'bot'):
        print("Sender is None or not a valid user object")
        return
    
    if current_status == "offline" and not sender.bot:
        user_id = event.sender_id
        current_time = time.time()

        # Check cooldown
        if current_time - cooldown[user_id] < 600:  # 10 minutes
            print(f"Cooldown active for user {user_id}")
            return
        cooldown[user_id] = current_time

        try:
            await event.reply(
                message=OFFLINE_MESSAGE,
                parse_mode='html',
                link_preview=False
            )
            await event.react('⏳')
            print(f"Replied to user {user_id}")
        except Exception as e:
            print(f"Error replying or reacting: {e}")

async def update_presence():
    last_status = None
    while True:
        try:
            if last_status != current_status:
                await client(functions.account.UpdateProfileRequest(
                    about=ONLINE_MESSAGE if current_status == "online" else OFFLINE_MESSAGE
                ))
                last_status = current_status
                print(f"Profile updated: {current_status}")
        except Exception as e:
            print(f"Error updating profile: {e}")
        await asyncio.sleep(300)  # Update every 5 minutes

async def main():
    try:
        await client.start()
        me = await client.get_me()
        print(f"⚡️ Premium Self-Bot Active ⚡️\nUser: {me.first_name}\nID: {me.id}")
        asyncio.create_task(update_presence())
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Error during execution: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
from telethon import TelegramClient, events
import re
import hashlib
import os
import json

# ==== CONFIG ====
api_id = 29666972
api_hash = 'b690d5b50137aeb5da5bcd32b5f1dabe'

SOURCE_CHANNELS = [
    'CKoffers',
    'techglaredeals',
    'freekart',
    'idoffers',
    'everydaylimitlessdeals',
    'dealsmaster1'
]

TARGET_CHANNEL = 'LootLeloDeals'
AFFILIATE_TAG = 'lootlelodeals-21'
HASH_STORE_FILE = 'posted_hashes.json'

# ==== Load posted hashes ====
if os.path.exists(HASH_STORE_FILE):
    with open(HASH_STORE_FILE, 'r') as f:
        posted_hashes = set(json.load(f))
else:
    posted_hashes = set()

def save_hashes():
    with open(HASH_STORE_FILE, 'w') as f:
        json.dump(list(posted_hashes), f)

# ==== Amazon Link Modifier ====
def convert_amazon_link(text):
    amazon_regex = r"(https:\/\/(?:www\.)?amazon\.in\/[^\s)]+)"

    def replace_tag(url):
        url = re.sub(r'([&?])tag=[^&\s]*', '', url)
        url = re.sub(r'[?&]+$', '', url)
        if '?' in url:
            return url + '&tag=' + AFFILIATE_TAG
        else:
            return url + '?tag=' + AFFILIATE_TAG

    return re.sub(amazon_regex, lambda m: replace_tag(m.group(1)), text)

# ==== Start Telethon ====
client = TelegramClient('session', api_id, api_hash)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handle_new_message(event):
    try:
        msg_text = event.message.message or ""
        msg_text = msg_text.strip()
        msg_hash = hashlib.md5(msg_text.encode()).hexdigest()

        if msg_text and msg_hash in posted_hashes:
            print("Duplicate text message. Skipped.")
            return

        modified_text = convert_amazon_link(msg_text) if msg_text else None

        if event.message.media:
            await client.send_file(
                TARGET_CHANNEL,
                file=event.message.media,
                caption=modified_text
            )
        else:
            if modified_text:
                await client.send_message(TARGET_CHANNEL, modified_text)

        if msg_text:
            posted_hashes.add(msg_hash)
            save_hashes()

        print("Message forwarded.")
    except Exception as e:
        print("Error:", e)

print("Bot is running...")
client.start()
client.run_until_disconnected()
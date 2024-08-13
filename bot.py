from pyrogram import Client, filters

app = Client(
    "besharam_bot",
    api_id=21192093,
    api_hash="1602d34e006e904834a1908bd8115834",
    bot_token="7447839522:AAGmyjV-1AKjJrssojrc-KtRQ5m2k1RNI48"
)

@app.on_message(filters.command("start") & filters.private)
async def private_start_cmd(client, message):
    return await message.reply(f"Hello {message.from_user.mention}!")

app.run()

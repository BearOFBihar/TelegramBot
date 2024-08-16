import time
from collections import defaultdict
from pyrogram import Client, filters
import requests
import random
from pyrogram.enums import PollType
from pyrogram.errors import BadRequest, FloodWait, RPCError
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

app = Client(
    "Kittu_bot",
    api_id=21192093,
    api_hash="1602d34e006e904834a1908bd8115834",
    bot_token="7381195643:AAHx3413-ti14NMKKeoWDhRqCFvw9C9DEsU"
)

API_ENDPOINT = "https://api.qewertyy.dev/models?model_id=23&prompt=Generate a quiz question with 4 options based on the topic '{q}' and difficulty '{d}'. Exact Format: Question: <question>\n 1) \n2) \n3) \n4)\nAnswer: <correct_option_number_only> Include nothing else."

HEADERS = {
    'accept': 'application/json'
}

VALID_DIFFICULTY_LEVELS = ["easy", "medium", "hard", "insane"]
RANDOM_TOPICS = ["Movies", "Science", "History", "Geography", "Literature", "Music", "Sports", "Technology", "Anime", "Series", "Celebrity", "Actors", "Singers", "Country", "Mythology", "Comics", "Heros", "Villains", "Manga", "Animals", "birds"]

cooldown_times = defaultdict(int)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user = message.from_user
    gif = "https://graph.org/file/13229ca00d888c3c49cba.mp4"
    txt = f"{user.mention}, thanks for starting me! I'll be in your care from now on. My name is Kittu and I've been made using @LexicaAPI. I can send you quiz polls on any topic you want! Add me to your group and let the fun begin!"
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Add Me", url="http://t.me/KittuQuizBot?startgroup=true")],
            [
                InlineKeyboardButton("🚑 Support", url="https://t.me/KittuTalks"),
                InlineKeyboardButton("❓Help", url="https://t.me/KittuQuizChannel")
            ]
        ]
    )
    await client.send_video(message.chat.id, gif, caption=txt, reply_markup=keyboard)

async def get_question(q, d):
    prompt = API_ENDPOINT.format(q=q, d=d)
    response = requests.post(prompt, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data.get('content', [{'text': 'No content found'}])  # Return the content part of the response
    else:
        return [{'text': 'Error fetching questions.'}]

@app.on_message(filters.command("quiz") & filters.group)
async def send_quiz(client, message):
    chat_id = message.chat.id

    # Check cooldown
    current_time = time.time()
    if current_time - cooldown_times[chat_id] < 10:
        return
    cooldown_times[chat_id] = current_time
    
    parts = message.text.split()[1:]
    
    if len(parts) == 1 and parts[0].lower() == "random":
        q = random.choice(RANDOM_TOPICS)
        d = random.choice(VALID_DIFFICULTY_LEVELS)
    elif len(parts) < 2:
        await message.reply("Wrong format!\nExample:\n  /quiz Movies Hard\nOr use /quiz random")
        return
    else:
        q = " ".join(parts[:-1])
        d = parts[-1].lower()
        
        if d not in VALID_DIFFICULTY_LEVELS:
            await message.reply("Invalid quiz level!\nPlease choose one of the following levels:\n1) Easy 😀\n2) Medium 😬\n3) Hard 😱\n4) Insane 💀")
            return
    
    questions_data = await get_question(q, d)
    
    for question_data in questions_data:
        x = question_data['text']

        if "Error" in x:
            await message.reply("Failed to fetch questions from the API.")
            return

        # Clean up the response and handle multiple questions
        questions = [q.strip() for q in x.split("Question: ") if q.strip()]
        
        if not questions:
            await message.reply("No valid question found.")
            return
        
        for question_block in questions:
            try:
                question_part = question_block.split("Answer:")[0].strip()
                answer_part = question_block.split("Answer:")[1].strip()

                lines = [line.strip() for line in question_part.split("\n") if line.strip()]
                if len(lines) < 5:
                    await message.reply("Invalid question format received.")
                    continue

                question = lines[0]
                option_1 = lines[1]
                option_2 = lines[2]
                option_3 = lines[3]
                option_4 = lines[4]

                options = [option_1, option_2, option_3, option_4]

                correct_option_id = int(answer_part) - 1  # Assuming the answer part is an integer corresponding to the correct option

                try:
                    # Send the poll
                    await client.send_poll(
                        chat_id=message.chat.id,
                        question=question,
                        options=options,
                        type=PollType.QUIZ,
                        correct_option_id=correct_option_id,
                        is_anonymous=False
                    )
                except BadRequest as e:
                    pass
            except (IndexError, RPCError) as e:
                pass
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except Exception as e:
                pass

if __name__ == "__main__":
    app.run()
                

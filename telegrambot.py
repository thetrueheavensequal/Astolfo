import telegram
import requests
import json
import os
import io
import re
import base64
import random
from PIL import Image
from pathlib import Path
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters
from telegram import Bot, InputFile
from pyrogram import Client, filters
from pyrogram.types import *
from dotenv import load_dotenv
from PIL import Image, PngImagePlugin





load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ENDPOINT = os.getenv("ENDPOINT")
PERIOD_IGNORE = os.getenv("PERIOD_IGNORE")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SD_URL = os.getenv("SD_URL")




def split_text(text):
    parts = re.split(r'\n[a-zA-Z]', text)
    return parts
def upload_character(json_file, img, tavern=False):
    json_file = json_file if type(json_file) == str else json_file.decode('utf-8')
    data = json.loads(json_file)
    outfile_name = data["char_name"]
    i = 1
    while Path(f'Characters/{outfile_name}.json').exists():
        outfile_name = f'{data["char_name"]}_{i:03d}'
        i += 1
    if tavern:
        outfile_name = f'TavernAI-{outfile_name}'
    with open(Path(f'Characters/{outfile_name}.json'), 'w') as f:
        f.write(json_file)
    if img is not None:
        img = Image.open(io.BytesIO(img))
        img.save(Path(f'Characters/{outfile_name}.png'))
    print(f'New character saved to "Characters/{outfile_name}.json".')
    return outfile_name

def upload_tavern_character(img, name1, name2):
    _img = Image.open(io.BytesIO(img))
    _img.getexif()
    decoded_string = base64.b64decode(_img.info['chara'])
    _json = json.loads(decoded_string)
    _json = {"char_name": _json['name'], "char_persona": _json['description'], "char_greeting": _json["first_mes"], "example_dialogue": _json['mes_example'], "world_scenario": _json['scenario']}
    _json['example_dialogue'] = _json['example_dialogue'].replace('{{user}}', name1).replace('{{char}}', _json['char_name'])
    return upload_character(json.dumps(_json), img, tavern=True)


def get_prompt(conversation_history, user, text):
    return {
        "prompt": conversation_history + f"{user}: {text}\n{char_name}:",
        "use_story": False,
        "use_memory": False,
        "use_authors_note": False,
        "use_world_info": False,
        "max_context_length": 2048,
        "max_length": 120,
        "rep_pen": 1.1,
        "rep_pen_range": 1024,
        "rep_pen_slope": 0.7,
        "temperature": 0.69,
        "tfs": 1,
        "top_a": 0,
        "top_k": 0,
        "top_p": 0.9,
        "typical": 1,
        "sampler_order": [6, 0, 1, 2, 3, 4, 5],
        "singleline": True,
        #"sampler_seed": 69420,   #set the seed
        #"sampler_full_determinism": True,     #set it so the seed determines generation content
        "frmttriminc": True,
        "frmtrmblln": False
    }

characters_folder = 'Characters'
cards_folder = 'Cards'
characters = []

# Check the Cards folder for cards and convert them to characters
try:
    for filename in os.listdir(cards_folder):
        if filename.endswith('.png'):
            with open(os.path.join(cards_folder, filename), 'rb') as read_file:
                img = read_file.read()
                name1 = 'User'
                name2 = 'Character'
                tavern_character_data = upload_tavern_character(img, name1, name2)
            with open(os.path.join(characters_folder, tavern_character_data + '.json')) as read_file:
                character_data = json.load(read_file)
            read_file.close()
            os.rename(os.path.join(cards_folder, filename), os.path.join(cards_folder, 'Converted', filename))
except:
    pass

# Load character data from JSON files in the character folder
for filename in os.listdir(characters_folder):
    if filename.endswith('.json'):
        with open(os.path.join(characters_folder, filename)) as read_file:
            character_data = json.load(read_file)
            # Check if there is a corresponding image file for the character
            image_file_jpg = f"{os.path.splitext(filename)[0]}.jpg"
            image_file_png = f"{os.path.splitext(filename)[0]}.png"
            if os.path.exists(os.path.join(characters_folder, image_file_jpg)):
                character_data['char_image'] = os.path.join(characters_folder, image_file_jpg)
            elif os.path.exists(os.path.join(characters_folder, image_file_png)):
                character_data['char_image'] = os.path.join(characters_folder, image_file_png)

            characters.append(character_data)

# Print a list of characters and let the user choose one
for i, character in enumerate(characters):
    print(f"{i+1}. {character['char_name']}")
selected_char = int(input("Please select a character: ")) - 1
data = characters[selected_char]
# Get the character name, greeting, and image
char_name = data["char_name"]
char_greeting = data["char_greeting"]
#char_dialogue = data["char_greeting"]
char_image = data.get("char_image")
print("Loaded up " + char_name)
num_lines_to_keep = 20
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
global conversation_history
with open(f'conversation_history_{char_name}.txt', 'a+') as file:
    file.seek(0)
    # Read the contents of the file
    chathistory = file.read()
conversation_history = f"{char_name}'s Persona: {data['char_persona']}\n" + \
                            f"World Scenario: {data['world_scenario']}\n" + \
                            f'<START>\n' + \
                            f'f"{char_name}: {char_greeting}\n{chathistory}'

# SET BOT PROFILE PIC

######

#---Telegram blocks Bot to Bot Messages, making this code not work---#


# Send the "/setuserpic" command to the "@BotFather" account
#bot.send_message(chat_id='93372553', text='/setuserpic')
#if os.path.exists(os.path.join(characters_folder, image_file_jpg)):
#    with open(os.path.join(characters_folder, image_file_jpg), 'rb') as f:
#        bot.send_photo(chat_id='93372553', photo=f)
#elif os.path.exists(os.path.join(characters_folder, image_file_png)):
#    with open(os.path.join(characters_folder, image_file_png), 'rb') as f:
#        bot.send_photo(chat_id='93372553', photo=f)
#else:
#    print("Profile photo not found.")

# Set the Botname via the "@BotFather" account
#bot.send_message(chat_id='93372553', text='/setname' + char_name)

#---Telegram blocks Bot to Bot Messages, making this code not work---#

######







# Escape reserved characters to allow markdown formatting
def escape_message(message):
    reserved_chars = r'*[]()~`>#+-=|{}.!'
    escaped_chars = [f'\\{c}' if c in reserved_chars else c for c in message]
    return ''.join(escaped_chars)


# Define the function to handle incoming messages
def handle_message(update, context):
    global conversation_history
    # Get the incoming message text
    user_message = update.message.text

    # Generate a prompt using the conversation history, user, and message text
    prompt = get_prompt(conversation_history, update.message.from_user.first_name, user_message)

    # Send the prompt to KoboldAI and get the response
    response = requests.post(f"{ENDPOINT}/api/v1/generate", json=prompt)

    # Parse the response and get the generated text
    if response.status_code == 200:
        results = response.json()['results']
        text = results[0]['text']
        response_text = split_text(text)[0]
        esc_response_text = split_text(text)[0]

        # Update the conversation history with the user message and bot response
        response_text = response_text.replace("  ", " ")        
        conversation_history += f"{update.message.from_user.first_name}: {user_message}\n{char_name}: {response_text}\n"
        # Append conversation to text file
        with open(f'conversation_history_{char_name}.txt', "a") as f:
            f.write(f"{update.message.from_user.first_name}: {user_message}\n{char_name}: {response_text}\n")
        

        # checks if acting out an action and changes * to _
        response_text = response_text.replace("*", "_")


        # escapes text
        esc_response_text = escape_message(response_text)



        # Send the response back to the user
        context.bot.send_message(chat_id=update.effective_chat.id, text=esc_response_text, parse_mode="MarkdownV2")

# Set up the dispatcher to handle incoming messages
dispatcher = updater.dispatcher

# Add the handler to the dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Start the bot
updater.start_polling()




################# GENERATE IMAGES FROM STABLE DIFFUSION API #################

botSD = Client(
    "stable",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TELEGRAM_BOT_TOKEN
)

@botSD.on_message(filters.command(["draw"]))
def draw(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format : /draw < text to image >")
        return
    msg = msgs[1]

    K = message.reply_text("searching my phone, one sec")

    payload = {
        "prompt": msg,
        "steps": 50,
        "batch_size": 1,
        "n_iter": 1,
        "cfg scale": 7,
        "width": 360, # Feel free to change these if your GPU is not limited
        "height": 640, # Feel free to change these if your GPU is not limited
       # "enable_hr': false,
       # "denoising_strength": 0,
       # "firstphase_width": 0,
       # "firstphase_height": 0,
       # "styles": [
       #     "string"
       # ],
        "seed": -1,
        "subseed": -1,
        "subseed_strength": 0,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
        "restore_faces": True,
        "tiling": False,
        "negative prompt": "Out of frame, out of focus, morphed",
        "s_churn": 0,
        "s_tmax": 0,
        "s_tmin": 0,
        "s_noise": 1,
        "sampler_index": "DPM++ 2M Karras"
}

    r = requests.post(url=f'{SD_URL}/sdapi/v1/txt2img', json=payload).json()

    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars1 = "1234564890"
    gen1 = random.choice(chars)
    gen2 = random.choice(chars)
    gen3 = random.choice(chars1)
    gen4 = random.choice(chars)
    gen5 = random.choice(chars)
    gen6 = random.choice(chars)
    gen7 = random.choice(chars1)
    gen8 = random.choice(chars)
    gen9 = random.choice(chars)
    gen10 = random.choice(chars1)
    word = f"{message.from_user.id}-MOE{gen1}{gen2}{gen3}{gen4}{gen5}{gen6}{gen7}{gen8}{gen9}{gen10}"

    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))

        png_payload = {"image": "data:image/png;base64," + i}
        response2 = requests.post(url=f'{SD_URL}/sdapi/v1/png-info',
                                  json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(f'{word}.png', pnginfo=pnginfo)

        message.reply_photo(
            photo=f"{word}.png",
            caption=
            f"Prompt - **{msg}**\n **[{message.from_user.first_name}-Kun](tg://user?id={message.from_user.id})**\n"
        )
        os.remove(f"{word}.png")
        K.delete()


@botSD.on_message(filters.command(["start"], prefixes=["/", "!"]))
async def start(client, message):
    Photo = ""

    buttons = [[
        InlineKeyboardButton("Add to your group",
                             url="http://t.me/botname?startgroup=true"),
    ]]
    await message.reply_photo(
        photo=Photo,
        caption=
        f"Hello! I'm botname Ai and I can make pictures!\n\n/draw text to image",
        reply_markup=InlineKeyboardMarkup(buttons))


botSD.run()


###############################

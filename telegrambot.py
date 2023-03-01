import telegram
import requests
import json
import os
import io
from PIL import Image
from pathlib import Path
import re
import base64
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters
from telegram import Bot, InputFile

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ENDPOINT = os.getenv("ENDPOINT")
PERIOD_IGNORE = os.getenv("PERIOD_IGNORE")



def split_text(text):
    parts = re.split(r'\n[a-zA-Z]', text)
    return parts
def upload_character(json_file, img, tavern=False):
    json_file = json_file if type(json_file) == str else json_file.decode('utf-8')
    data = json.loads(json_file)
    outfile_name = data["char_name2"]
    i = 1
    while Path(f'Characters/{outfile_name}.json').exists():
        outfile_name = f'{data["char_name2"]}_{i:03d}'
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
    _json = {"char_name2": _json['name'], "char_persona": _json['description'], "char_greeting": _json["first_mes"], "example_dialogue": _json['mes_example'], "world_scenario": _json['scenario']}
    _json['example_dialogue'] = _json['example_dialogue'].replace('{{user}}', name1).replace('{{char}}', _json['char_name2'])
    return upload_character(json.dumps(_json), img, tavern=True)


def get_prompt(conversation_history, user, text):
    return {
        "prompt": conversation_history + f"{user}: {text}\n{char_name2}:",
        "use_story": False,
        "use_memory": False,
        "use_authors_note": False,
        "use_world_info": False,
        "max_context_length": 2048,
        "max_length": 120,
        "rep_pen": 1.1,
        "rep_pen_range": 1024,
        "rep_pen_slope": 0.7,
        "temperature": 0.5,
        "tfs": 1,
        "top_a": 0,
        "top_k": 0,
        "top_p": 0.9,
        "typical": 1,
        "sampler_order": [6, 0, 1, 2, 3, 4, 5],
        "frmttriminc": True,
        "frmtrmblln": True
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
    print(f"{i+1}. {character['char_name2']}")
selected_char = int(input("Please select a character: ")) - 1
data = characters[selected_char]
# Get the character name, greeting, and image
char_name2 = data["char_name2"]
char_greeting = data["char_greeting"]
#char_dialogue = data["char_greeting"]
char_image = data.get("char_image")
print("Loaded up " + char_name2)
num_lines_to_keep = 20
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
global conversation_history
conversation_history = f"{char_name2}'s Persona: {data['char_persona']}\n" + \
                            f"World Scenario: {data['world_scenario']}\n" + \
                            f'<START>\n' + \
                            f'f"{char_name2}: {char_greeting}\n'

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
#bot.send_message(chat_id='93372553', text='/setname' + char_name2)

#---Telegram blocks Bot to Bot Messages, making this code not work---#

######

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

        # Update the conversation history with the user message and bot response
        
        conversation_history += f"{update.message.from_user.first_name}: {user_message}\n{char_name2}: {response_text}\n"

        # Send the response back to the user
        context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

# Set up the dispatcher to handle incoming messages
dispatcher = updater.dispatcher

# Add the handler to the dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Start the bot
updater.start_polling()




# KoboldAI Integrated Telegram Chatbot
This is a Telegram bot that uses KoboldAI to host models such as Pygmalion-6B with a KoboldAI url. The bot supports json files and tavern cards but will not change its name and image automatically due to Telegram's bot-bot restrictions. 

![Screenshot from 2023-02-28 21-58-50 (1)](https://user-images.githubusercontent.com/80486540/222042223-ee874981-b43c-44f5-825b-164459e8403b.jpg)



# Instructions: 
>1. Clone the repo.

>2. Change the variables in the sample.env file then rename it to only ".env" in the same folder. This sets environment variables

>3. Run the bat or shell file

>4. Choose the character

![Choose](https://i.imgur.com/qY6ZpB8.png)


[Get more Characters](https://booru.plus/+pygmalion)
# More Info: 

TELEGRAM_BOT_TOKEN: You can get this from creating a bot in Telegram via the @BotFather. [Guide for setting that up](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0#create-a-new-telegram-bot-with-botfather)

ENDPOINT: Set the endpoint variable with the KoboldAI url you get from KoboldAI. This can either be from a locally ran instance, or a remote instance like [google collab](https://colab.research.google.com/drive/1ZvYq4GmjfsyIkcTQcrBhSFXs8vQLLMAS).

Look for this url in the google collab output:

![url example](https://raytracing-benchmarks.are-really.cool/5utGhMj.png)


If you're running locally, by default the endpoint is http://localhost:5000



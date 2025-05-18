# Easton Composite Squadron Discord bot

This repo hosts the source code for the bot used in the Easton Composite Squadron Discord server. It manages welcomes, logs, and other admin actions.

To run the bot, we'll need to do three things:

### 1. Setup the Environment
First, create a virtual env to install dependancies using this command:
```
python3 -m venv .venv
```

Next, we can activate the environment by using:
```
source .venv/bin/activate
```

Lastly, we need to install our dependancies with: 
```
pip install -r requirements.txt
```

### 2. Add Environment Variables
Create a file with the name `.env`. Add a single line containing the following:
```
TOKEN=YOUR_TOKEN_HERE
```
Make sure you replace `YOUR_TOKEN_HERE` with the token you obtained in the Discord developer portal.

### 3. Run the bot
The last step is to run the bot. We can do that with this command:
```
python3 bot.py
```
Congratulations, the bot is now running!
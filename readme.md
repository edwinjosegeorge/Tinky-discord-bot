# Custom Discord bot

This custom discord-python bot assigns roles to members joined at discord server. It looks and compares a list before verifying the roles. Helps to forming naming convention and simplify the registration process, deployed via heroku.

## Setting up the bot
1. Clone this repo
   ```shell
   git clone https://github.com/edwinjosegeorge/Tinky-discord-bot.git
   cd Tinky-discord-bot
   ```
2. Create virtual environment (optional)
   ```bash
   python3 -m pip install --user virtualenv
   python3 -m venv myBotEnv
   source myBotEnv/bin/activate
   ```
3. Install libraries
   ```bash
   pip install -r requirements.txt
   ```
4. Setup the config variables
   
   i.  Set up system variables (recommended)
    Create a file `.env` and add tokens. Replace `' ... '` with
    relevant info.
    ```shell
    SERVER_ID='the id of server'
    SERVER_NAME='name of server'
    BOT_TOKEN='token of your bot'
    DATABASE_URL='cloud database url'
    ```
   ii. Update settings.py file (not recommended)
    Update [settings.py](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/settings.py) to the following
    
    ```python
    SERVER_ID=int('the id of server')
    SERVER_NAME=str('name of server')
    BOT_TOKEN=str('token of your bot')
    DATABASE_URL=str('cloud database url')
    ```
    
   Config variables can be fetched from your deployment environment. To obtain bot config, visit Discord.py developers portal

5. Update and suite the DataBase constraints by modifying [`psqlHandler.py`](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/psqlHandler.py) where necessary.  
   Take care to modify the code to suite your roles and constraints. currently the bot will send a message to all un-verified members to start registration.

6. Run you bot
   ```bash
   python3 tinky.py
   ```

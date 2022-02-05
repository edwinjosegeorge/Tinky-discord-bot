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
   Note: include the environment directory in [.gitignore](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/.gitignore)
3. Install libraries
   ```bash
   pip install -r requirements.txt
   ```
4. Setup the config variables

   i.  Set up system variables (recommended)
    Create a file `.env` and add tokens.
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

5. Updating the code

   i. Update and suite the DataBase interactions at [`PSQL_hooks.py`](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/PSQL_hooks.py).
   ii. Update and suite Bot interactions at [BOT.py](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/BOT.py).
   iii. Update and suite the registration interaction with discord member at [memberProp.py](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/memberProp.py).
   iV. Update display messages at [messageBox.py](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/messageBox.py). Messages during registration process are save in [memberProp.py](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/memberProp.py).
   v. Update the discord-to-database interactions (the core rules) at [integrations.py](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/integrations.py)

6. Run you bot
   ```bash
   python3 BOT.py
   ```

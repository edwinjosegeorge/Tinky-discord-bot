# Custom Discord bot

This custom discord-python bot assigns roles to members joined at discord server. It looks and compares a list before verifying the roles. Helps to forming naming convention and simplify the registration process, deployed via heroku.

## Setting up the bot
1. Clone this repo
   ```shell
   git clone https://github.com/edwinjosegeorge/Tinky-discord-bot.git
   cd Tinky-discord-bot
   ```
2. Create virtual environment (optional, but recommended)
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
    Add the following to your shell/bash
    ```shell
    SERVER_ID='the id of server'
    SERVER_NAME='name of server'
    BOT_TOKEN='token of your bot'
    DATABASE_URL='cloud database url'
    SOCIAL_POST_CHANNEL='id of channel'
    ```
   ii. Update settings.py file (not recommended)
    Update [settings.py](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/settings.py) to the following

    ```python
    SERVER_ID=int('the id of server')
    SERVER_NAME=str('name of server')
    BOT_TOKEN=str('token of your bot')
    DATABASE_URL=str('cloud database url')
    SOCIAL_POST_CHANNEL=str("id of channel")
    ```

   Config variables can be fetched from your deployment environment. To obtain bot config, visit Discord.py developers portal

5. Updating the code

   * Update and suite the DataBase interactions at [database](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/database/). Details how to interface database.
   * Update and suite Bot interactions at [BOT.py](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/BOT.py). Details when, where and how the bot should be triggered.
   * Update and suite the registration interaction with discord member at [member](https://github.com/edwinjosegeorge/Tinky-discord-bot/tree/main/member).
   * Update display messages at [messageBox.py](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/messageBox.py). Messages during registration process are save in [member.messageBox.](https://github.com/edwinjosegeorge/Tinky-discord-bot/blob/main/member/messageBox.py).

6. Run you bot
   ```bash
   python3 BOT.py
   ```

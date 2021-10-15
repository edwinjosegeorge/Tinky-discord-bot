from decouple import config

DATABASE_URL = config("DATABASE_URL")
BOT_TOKEN = config('BOT_TOKEN')
SERVER_ID = config("SERVER_ID", cast=int)
SERVER_NAME = config('SERVER_NAME', default="")

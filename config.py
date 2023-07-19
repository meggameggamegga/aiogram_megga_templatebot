from environs import Env

env = Env()
env.read_env()


BOT_TOKEN=env.str('TOKEN_BOT')
ADMIN_ID=env.str('ADMIN_ID')
CLIENT_ID=env.str('CLIENT_ID')
URL_BOT = 'https://t.me/testertestcode_bot'
ACCESS_TOKEN=env.str('ACCESS_TOKEN')
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import database

# 환경변수 로드
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 데이터베이스 초기화
database.init_db()
database.seed_creatures()

# 봇 권한 설정 (Intents)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    # Cogs 로드
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('_'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded Cog: {filename}')
            except Exception as e:
                print(f'Failed to load Cog {filename}: {e}')

@bot.command(name='업데이트', help='(관리자용) 최신 코드를 당겨오고 봇을 재시작합니다.')
@commands.is_owner()
async def update_bot(ctx):
    await ctx.send("🔄 업데이트를 위해 봇을 재시작합니다...")
    await bot.close()

if __name__ == '__main__':
    if not TOKEN or TOKEN == 'your_token_here':
        print("Error: DISCORD_TOKEN이 설정되지 않았습니다. .env 파일을 확인해주세요.")
    else:
        bot.run(TOKEN)

import discord
from discord.ext import commands
import random
import asyncio
import database

# 임시 날씨 및 바이옴 목록
BIOMES = ['숲', '들판', '툰드라']
WEATHER_CONDITIONS = ['맑음', '비', '흐림', '악천후', '비 온 뒤 흐림']

class Explore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_user_or_create(self, user_id):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, coin, explore_count FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            conn.commit()
            user = (user_id, 0, 0)
        
        conn.close()
        return user

    def add_creature_to_inventory(self, user_id, creature_id):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (user_id, creature_id) VALUES (?, ?)", (user_id, creature_id))
        conn.commit()
        conn.close()

    @commands.command(name='탐색', help='새로운 지역을 탐색하여 생물을 포획합니다.')
    async def explore(self, ctx):
        user_id = ctx.author.id
        self.get_user_or_create(user_id)

        # 바이옴 3개 랜덤 선택 (중복 허용 또는 비허용)
        options = random.sample(BIOMES, min(3, len(BIOMES)))
        
        embed = discord.Embed(
            title="탐색 가능한 지역이 발견되었습니다.",
            description="이동할 지역의 번호를 입력하세요.",
            color=discord.Color.green()
        )
        
        for i, biome in enumerate(options, 1):
            embed.add_field(name=f"{i}. {biome}", value="무엇이 있을까요?", inline=False)
            
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content in ['1', '2', '3']

        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("탐색 시간이 초과되었습니다. 다시 시도해주세요.")
            return

        choice_idx = int(msg.content) - 1
        selected_biome = options[choice_idx]
        current_weather = random.choice(WEATHER_CONDITIONS)

        await ctx.send(f"**{selected_biome}**(으)로 이동합니다... (현재 날씨: {current_weather})")
        await asyncio.sleep(2) # 이동 연출
        
        # 등장 등급 결정
        # LR: 0.01%, UR: 1%, SR: 6%, R: 24.99%, N: 68%
        grade_roll = random.uniform(0, 100)
        if grade_roll <= 0.01:
            target_grade = 'LR'
        elif grade_roll <= 1.01:
            target_grade = 'UR'
        elif grade_roll <= 7.01:
            target_grade = 'SR'
        elif grade_roll <= 32.0:
            target_grade = 'R'
        else:
            target_grade = 'N'

        # 선택된 바이옴과 결정된 등급에 해당하는 생물 조회
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, grade, combat_power, trait, weather_condition FROM creatures WHERE biomes LIKE ? AND grade = ?", (f'%{selected_biome}%', target_grade))
        creatures = cursor.fetchall()
        conn.close()
        
        if not creatures:
            await ctx.send(f"앗, 무언가(예상 등급: **{target_grade}**) 지나간 것 같지만... 아직 도감에 기록되지 않은 미지의 생물이다!")
            return
            
        # 등장할 생물 선택
        encounter = random.choice(creatures)
        c_id, c_name, c_grade, c_power, c_trait, c_weather = encounter
        
        # 포획 시스템 (위험도 및 날씨에 따른 간단한 확률)
        catch_chance = 70 # 기본 확률
        
        # 날씨 보정 (임시)
        if current_weather in ['비', '악천후'] and '확률 감소' in c_weather:
            catch_chance -= 30
        
        encounter_embed = discord.Embed(
            title=f"앗! 야생의 **{c_name}**(이)가 나타났다!",
            description=f"등급: {c_grade} | 전투력: {c_power} | 특성: {c_trait}",
            color=discord.Color.orange()
        )
        encounter_embed.set_footer(text="포획 시도 중...")
        await ctx.send(embed=encounter_embed)
        
        await asyncio.sleep(2) # 포획 연출
        
        success = random.randint(1, 100) <= catch_chance
        
        if success:
            self.add_creature_to_inventory(user_id, c_id)
            await ctx.send(f"🎉 **{c_name}** 포획 성공! 도감에 등록되었습니다.")
        else:
            await ctx.send(f"💨 아앗... **{c_name}**(이)가 도망쳤습니다.")

    @commands.command(name='도감', help='현재 보유 중인 생물 도감을 확인합니다.')
    async def inventory(self, ctx):
        user_id = ctx.author.id
        
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.name, c.grade, COUNT(i.id) 
            FROM inventory i
            JOIN creatures c ON i.creature_id = c.id
            WHERE i.user_id = ?
            GROUP BY c.id
        ''', (user_id,))
        items = cursor.fetchall()
        conn.close()
        
        if not items:
            await ctx.send(f"{ctx.author.name}님의 도감은 텅 비어있습니다. `./탐색`을 통해 생물을 포획해보세요!")
            return
            
        embed = discord.Embed(
            title=f"📖 {ctx.author.name}님의 생물 도감",
            color=discord.Color.blue()
        )
        
        for name, grade, count in items:
            embed.add_field(name=f"{name} [{grade}]", value=f"보유 수: {count}마리", inline=True)
            
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Explore(bot))

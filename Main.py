import discord
from discord.ext import commands
import os
import asyncio
import aiohttp
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# إعدادات أوقات الصلاة - الرياض افتراضي
CITY = "Riyadh"
COUNTRY = "Saudi Arabia"

QURAN_RADIOS = {
    "مكة": "https://stream.radiojar.com/8s5u5tpdtwzuv",
    "قرآن": "https://Qurango.net/radio/mix",
    "السديس": "https://backup.qurango.net/radio/mix"
}

@bot.event
async def on_ready():
    print(f"✅ ONLINE - {bot.user} - يعمل في السعودية!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!salat | !quran"))

@bot.command(name="salat")
async def salat(ctx, city: str = None):
    city_name = city or CITY
    try:
        async with aiohttp.ClientSession() as session:
            url = f"http://api.aladhan.com/v1/timingsByCity?city={city_name}&country={COUNTRY}&method=4"
            async with session.get(url) as resp:
                data = await resp.json()
                timings = data['data']['timings']
                
                embed = discord.Embed(title=f"🕌 أوقات الصلاة - {city_name}", color=0x00ff00, timestamp=datetime.now())
                embed.add_field(name="الفجر", value=timings['Fajr'], inline=True)
                embed.add_field(name="الظهر", value=timings['Dhuhr'], inline=True)
                embed.add_field(name="العصر", value=timings['Asr'], inline=True)
                embed.add_field(name="المغرب", value=timings['Maghrib'], inline=True)
                embed.add_field(name="العشاء", value=timings['Isha'], inline=True)
                embed.set_footer(text="طريقة أم القرى - السعودية")
                await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ ما قدرت اجيب الأوقات: {e}")

@bot.command(name="quran")
async def quran(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ ادخل روم صوتي أول!")
    
    channel = ctx.author.voice.channel
    vc = ctx.voice_client or await channel.connect()
    
    # راديو قرآن مكة
    source = discord.FFmpegPCMAudio("https://stream.radiojar.com/8s5u5tpdtwzuv")
    vc.play(source)
    await ctx.send("📻 **شغلت راديو القرآن - مكة** 🕋")

@bot.command(name="stop")
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ تم الايقاف")
    else:
        await ctx.send("ما انا مشغل شي")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 {round(bot.latency*1000)}ms - شغال في السعودية ✅")

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("❌ حط متغير TOKEN في Railway!")
else:
    bot.run(TOKEN)

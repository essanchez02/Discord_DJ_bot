import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
from musicProfiles.profile_utils import get_or_create_profile

# ====================== Setup ======================
# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Basic setup for all discord bots
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Youtube-DL and FFmpeg setup
ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
#====================== Discord Commands ======================
@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')

@bot.command()
async def join(ctx):
    # Check if the user is in a voice channel
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        # Ensure sure everyone in channel has a music profile
        if ctx.author.voice and ctx.author.voice.channel:
            voice_members = ctx.author.voice.channel.members
            for member in voice_members:
                # Skip the bot
                if member.bot:
                    continue
                get_or_create_profile(member)
    else:
        await ctx.send("You need to be in a voice channel.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel.")

@bot.command()
async def play(ctx, url):
    # Join the voice channel if not already connected
    if not ctx.voice_client:
        await ctx.invoke(join)

    info = ytdl.extract_info(url, download=False)
    url2 = info['url']

    # Use FFmpegPCMAudio for volume control
    source = discord.FFmpegPCMAudio(url2, **ffmpeg_options)
    source = discord.PCMVolumeTransformer(source, volume=0.08)  # 8% volume

    ctx.voice_client.stop()
    ctx.voice_client.play(source, after=lambda e: print(f'Done: {e}'))

    await ctx.send(f'🎶 Now playing: **{info["title"]}**')

bot.run(TOKEN)

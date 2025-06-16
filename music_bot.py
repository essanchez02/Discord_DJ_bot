import discord
from discord.ext import commands
import youtube_dl

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
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
    if not ctx.voice_client:
        await ctx.invoke(join)

    info = ytdl.extract_info(url, download=False)
    url2 = info['url']
    source = await discord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)

    ctx.voice_client.stop()
    ctx.voice_client.play(source, after=lambda e: print(f'Done: {e}'))

    await ctx.send(f'🎶 Now playing: **{info["title"]}**')

bot.run("YOUR_DISCORD_BOT_TOKEN")

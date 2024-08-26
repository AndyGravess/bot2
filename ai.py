import discord
import asyncio
from discord.ext import commands
from gtts import gTTS
from io import BytesIO
import os
import tempfile
import ffmpeg

# Botunuzu başlatın
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} olarak giriş yaptı.')

@bot.command(name='katıl')
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
            await ctx.send('Kanala katıldım!')
        else:
            await ctx.send('Zaten bir ses kanalındayım!')
    else:
        await ctx.send('Bir ses kanalına bağlı olmalısınız!')

@bot.command(name='söyle')
async def speak(ctx):
    if ctx.voice_client:
        if ctx.message.attachments:
            # İlk ekli dosyayı al
            attachment = ctx.message.attachments[0]
            file_extension = attachment.filename.split('.')[-1].lower()

            if file_extension in ['mp3', 'wav', 'm4a']:
                # Ses dosyasını geçici bir dosyaya kaydet
                file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}')
                await attachment.save(file.name)

                # Ses dosyasını Discord sesli kanalda çal
                ctx.voice_client.stop()
                ctx.voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=file.name))

                # Oynatma işlemi bitene kadar bekle
                while ctx.voice_client.is_playing():
                    await asyncio.sleep(1)

                # Geçici dosyayı sil
                os.remove(file.name)
                await ctx.send('Ses dosyasını oynattım!')

            elif file_extension in ['mp4', 'mov']:
                # Video dosyasından ses çıkarma işlemi
                file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}')
                await attachment.save(file.name)

                audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                audio_file_path = audio_file.name

                # FFmpeg kullanarak ses çıkarma işlemi
                ffmpeg.input(file.name).output(audio_file_path).run()

                # Ses dosyasını Discord sesli kanalda çal
                ctx.voice_client.stop()
                ctx.voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=audio_file_path))

                # Oynatma işlemi bitene kadar bekle
                while ctx.voice_client.is_playing():
                    await asyncio.sleep(1)
                
                # Geçici dosyaları sil
                os.remove(file.name)
                os.remove(audio_file_path)
                await ctx.send('Videonun sesini oynattım!')
            else:
                await ctx.send('Desteklenmeyen dosya türü!')
        else:
            # Sadece mesaj içeriğini oku
            text = ctx.message.content.replace('!söyle', '').strip()
            if text:
                tts = gTTS(text=text, lang='tr')
                audio_stream = BytesIO()
                tts.write_to_fp(audio_stream)
                audio_stream.seek(0)

                audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                audio_file_path = audio_file.name
                with open(audio_file_path, 'wb') as f:
                    f.write(audio_stream.read())

                # Ses dosyasını Discord sesli kanalda çal
                ctx.voice_client.stop()
                ctx.voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=audio_file_path))

                # Oynatma işlemi bitene kadar bekle
                while ctx.voice_client.is_playing():
                    await asyncio.sleep(1)

                # Geçici dosyayı sil
                os.remove(audio_file_path)
                await ctx.send('Yazıyı sesli olarak okudum!')
            else:
                await ctx.send('Lütfen bir yazı yazın veya bir dosya ekleyin!')
    else:
        await ctx.send('Önce bir ses kanalına katılmalısınız!')

@bot.command(name='ayrıl')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('Ses kanalından ayrıldım!')
    else:
        await ctx.send('Bir ses kanalında değilim!')

# Botunuzu çalıştırın
bot.run('MTI1MDA3NjE2MjAyNjI0MjE2Mw.GdJQon.wBMnP6h_Ni_eS-GUbPhI4BQSYX24fipsPE-7kI')  # Tokeninizi çevre değişkeninden alacak şekilde ayarlayın

# Botunuzu çalıştırın

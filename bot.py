import discord
from discord.ext import commands
import config
import random

intents = discord.Intents.default()
intents.members = True  # Bật quyền để bot có thể xem thành viên
intents.message_content = True  # Bật quyền để bot có thể xem nội dung tin nhắn

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot đã sẵn sàng với tên {bot.user}')

@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.id == config.GUILD_ID:
        channel = bot.get_channel(config.WELCOME_CHANNEL_ID)
        if channel:
            await channel.send(f'Chào mừng {member.mention} đến với server {guild.name}!')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Chào {ctx.author.mention}!')

@bot.command()
async def rand(ctx):
    random_number = random.randint(1, 100)
    await ctx.send(f'Số ngẫu nhiên là: {random_number}')

@bot.command()
async def list(ctx):
    commands_list = [cmd.name for cmd in bot.commands]
    commands_str = ', '.join(commands_list)
    await ctx.send(f'Danh sách các lệnh có sẵn :[ {commands_str} ]')

@bot.command()
async def thele(ctx):
    thele_link = ""  # Thay thế bằng đường link thực tế
    await ctx.send(f'Thể lệ: {thele_link}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Lệnh không tồn tại. Vui lòng thử lại.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Thiếu đối số cần thiết. Vui lòng kiểm tra lại lệnh.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Đối số không hợp lệ. Vui lòng kiểm tra lại lệnh.")
    else:
        await ctx.send(f"Đã xảy ra lỗi: {error}")
        print(f"Đã xảy ra lỗi: {error}")

bot.run(config.TOKEN)

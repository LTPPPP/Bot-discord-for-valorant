import discord
import re
from datetime import datetime, timedelta
import asyncio

def read_toxic_words(file_path):
    toxic_words = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():
                toxic_words.append(line.strip())
    return toxic_words

def setup_events(bot):
    # Lưu trữ số lần vi phạm của người dùng
    user_violations = {}

    @bot.event
    async def on_ready():
        print(f'Bot đã sẵn sàng với tên {bot.user}')

    # Đọc danh sách từ độc hại từ file
    toxic_words_file = 'toxic/toxic.txt'
    toxic_words = read_toxic_words(toxic_words_file)

    @bot.event
    async def on_member_join(member):
        guild = member.guild
        welcome_channels = [channel for channel in guild.text_channels if "welcome" in channel.name.lower()]
        if welcome_channels:
            for channel in welcome_channels:
                await channel.send(
                    f'Chào mừng {member.mention} đến với server {guild.name}! Vui lòng sử dụng lệnh /choose_role để chọn role của bạn.')

    @bot.event
    async def on_message(message):
        # Kiểm tra nội dung tin nhắn
        pattern = re.compile(r'\b(?:' + '|'.join(toxic_words) + r')\b', re.IGNORECASE)
        if pattern.search(message.content.lower()):
            # Tăng số lần vi phạm của người dùng
            if message.author.id in user_violations:
                user_violations[message.author.id] += 1
            else:
                user_violations[message.author.id] = 1

            # Nếu số lần vi phạm đạt 3, ban người dùng
            if user_violations[message.author.id] >= 3:
                try:
                    await message.author.ban(reason="Liên tục sử dụng ngôn ngữ độc hại")
                    await message.channel.send(f"{message.author.mention} đã bị ban 1 phút do sử dụng ngôn ngữ độc hại liên tục.")
                    user_violations[message.author.id] = 0
                    # Huỷ ban sau 1 phút
                    await asyncio.sleep(60)
                    await message.author.unban(reason="Thời gian ban đã hết")
                except discord.Forbidden:
                    await message.channel.send(f"Không thể ban {message.author.mention} do thiếu quyền.")
            else:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention}, ey ey chửi thề nói bậy gì đó, tin không kick bây giờ đóooooooo!!!!!")

        await bot.process_commands(message)

    return user_violations
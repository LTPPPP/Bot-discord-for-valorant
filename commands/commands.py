# commands/commands.py
import discord
from discord import app_commands
from discord.ext import commands
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import webbrowser
from config import client_id, client_secret

def setup_commands(bot):

    # Authenticate with Spotify API
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # hello command
    @bot.tree.command(name="hello", description="Chào hỏi người dùng")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f'Chào {interaction.user.mention}!')

    # help command
    @bot.tree.command(name="help", description="Trợ giúp")
    async def help_command(interaction: discord.Interaction):
        await interaction.response.send_message('Nếu bạn muốn trợ giúp hãy truy cập vào mục dicusion và đặt câu hỏi')

    # list command
    @bot.tree.command(name="list", description="Hiển thị danh sách các lệnh")
    async def list_commands(interaction: discord.Interaction):
        commands_list = [cmd.name for cmd in bot.tree.get_commands()]
        commands_str = ', '.join(commands_list)
        await interaction.response.send_message(f'Danh sách các lệnh có sẵn: [ {commands_str} ]')

    # thele command
    @bot.tree.command(name="thele", description="Hiển thị link thể lệ")
    async def thele(interaction: discord.Interaction):
        thele_link = "https://docs.google.com/document/d/1q4-N1CoKzg1P49aXt-8Qjh-uTC30Mljm1EX6qfPCwW0/edit?usp=sharing"
        await interaction.response.send_message(f'Thể lệ: {thele_link}')

    # rand command
    @bot.tree.command(name="rand", description="Random giữa hai đội")
    async def rand(interaction: discord.Interaction, input_str: str):
        try:
            count = 0
            team1, team2 = input_str.split(';')
            team1 = team1.strip()
            team2 = team2.strip()

            results = []
            for _ in range(5):
                choice = random.choice([team1, team2])
                if choice == team1:
                    count += 1
                results.append(choice)

            results_str = ', '.join(results)
            total_str = team1 if count > 5 - count else team2
            await interaction.response.send_message(f'Kết quả random 5 lần: {results_str}\nKết quả cuối cùng: {total_str}')
        except ValueError:
            await interaction.response.send_message("Vui lòng nhập đúng định dạng: /rand team1; team2")

    # mute command
    @bot.tree.command(name="mute", description="Tắt/bật âm thanh thông báo cho kênh (chỉ dành cho admin)")
    @commands.has_permissions(administrator=True)
    async def toggle_mute(interaction: discord.Interaction, channel: discord.TextChannel):
        if channel.id in bot.muted_channels:
            bot.muted_channels.remove(channel.id)
            await interaction.response.send_message(f"Đã bật âm thanh thông báo cho kênh {channel.mention}")
        else:
            bot.muted_channels.add(channel.id)
            await interaction.response.send_message(f"Đã tắt âm thanh thông báo cho kênh {channel.mention}")

    # set_role command
    @bot.tree.command(name="set_role", description="Set role cho nhiều người dùng")
    @commands.has_permissions(manage_roles=True, administrator=True)
    async def set_role(interaction: discord.Interaction, users_and_role: str):
        try:
            users_str, role_name = users_and_role.split(';')
            users = [user.strip() for user in users_str.split()]
            role_name = role_name.strip()

            role = discord.utils.get(interaction.guild.roles, name=role_name)
            if not role:
                await interaction.response.send_message(f"Không tìm thấy role '{role_name}'.")
                return

            success_count = 0
            for user_mention in users:
                user_id = int(user_mention.strip('<@!>'))
                member = interaction.guild.get_member(user_id)
                if member:
                    await member.add_roles(role)
                    success_count += 1

            await interaction.response.send_message(f"Đã set role {role.name} cho {success_count}/{len(users)} người dùng.")
        except ValueError:
            await interaction.response.send_message("Vui lòng nhập đúng định dạng: /set_role @user1 @user2 @user3 ; TênRole")
        except discord.Forbidden:
            await interaction.response.send_message("Bot không có đủ quyền để thực hiện hành động này.")
        except Exception as e:
            await interaction.response.send_message(f"Đã xảy ra lỗi: {str(e)}")

    # ping command
    @bot.tree.command(name="ping", description="Kiểm tra ping của bot")
    async def ping_command(interaction: discord.Interaction):
        latency = bot.latency * 1000
        await interaction.response.send_message(f'Ping của bot là {latency}ms')

    # clear command
    @bot.tree.command(name="clear", description="Xóa tin nhắn")
    @commands.has_permissions(manage_messages=True, administrator=True)
    async def clear(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 1000]):
        try:
            await interaction.response.defer(ephemeral=True)
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.followup.send(f"Đã xóa {len(deleted)} tin nhắn.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("Bot không có đủ quyền để xóa tin nhắn.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"Đã xảy ra lỗi khi xóa tin nhắn: {str(e)}", ephemeral=True)


    # music command
    @bot.tree.command(name="music", description="Phát một bài hát ngẫu nhiên từ top 50 Việt Nam trên Spotify")
    async def music(interaction: discord.Interaction):
        try:
            # Get the top 50 tracks in Vietnam
            top_50_tracks = sp.playlist_tracks('37i9dQZEVXbLdGSmz6xilI', limit=50)
            tracks = [(track['track']['name'], track['track']['external_urls']['spotify']) for track in top_50_tracks['items']]

            # Choose a random track
            random_track_name, random_track_uri = random.choice(tracks)

            # Send the track name and Spotify link to the user
            await interaction.response.send_message(f"Playing: [{random_track_name}]({random_track_uri})\nClick the link to listen on Spotify!")
        except Exception as e:
            await interaction.response.send_message(f"Đã xảy ra lỗi khi phát nhạc: {str(e)}")


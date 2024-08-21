import discord
from discord import app_commands
from discord.ext import commands
import random
import logging
from config import TOKEN  # Ensure you have your TOKEN stored securely in a config file

# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Define intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

# Define bot class
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.muted_channels = set()

    async def setup_hook(self):
        logging.debug("Starting command sync...")
        try:
            # Sync commands with Discord
            synced = await self.tree.sync()
            logging.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logging.error(f"Failed to sync commands: {e}")

# Initialize bot
bot = MyBot()

# Bot event when it's ready
@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')

# Welcome message when a new member joins
@bot.event
async def on_member_join(member):
    guild = member.guild
    welcome_channels = [channel for channel in guild.text_channels if "welcome" in channel.name.lower()]
    if welcome_channels:
        for channel in welcome_channels:
            await channel.send(
                f'Welcome {member.mention} to {guild.name}! Please use /choose_role to select your role.')

# Slash command for saying hello
@bot.tree.command(name="hello", description="Greet the user")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hello {interaction.user.mention}!')

# Slash command for help
@bot.tree.command(name="help", description="Provide help")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message('For help, please visit the discussion section and ask your question.')

# Slash command to list available commands
@bot.tree.command(name="list", description="Display a list of available commands")
async def list_commands(interaction: discord.Interaction):
    commands_list = [cmd.name for cmd in bot.tree.get_commands()]
    commands_str = ', '.join(commands_list)
    await interaction.response.send_message(f'Available commands: [ {commands_str} ]')

# Slash command to display a rule link
@bot.tree.command(name="thele", description="Display the rule link")
async def thele(interaction: discord.Interaction):
    thele_link = "https://docs.google.com/document/d/1q4-N1CoKzg1P49aXt-8Qjh-uTC30Mljm1EX6qfPCwW0/edit?usp=sharing"
    await interaction.response.send_message(f'Rules: {thele_link}')

# Slash command to randomize between two teams
@bot.tree.command(name="rand", description="Randomly choose between two teams")
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
        await interaction.response.send_message(f'Random results (5 times): {results_str}\nFinal result: {total_str}')
    except ValueError:
        await interaction.response.send_message("Please enter the correct format: /rand team1; team2")

# Slash command to mute/unmute a channel
@bot.tree.command(name="mute", description="Mute/unmute a channel (admin only)")
@commands.has_permissions(administrator=True)
async def toggle_mute(interaction: discord.Interaction, channel: discord.TextChannel):
    if channel.id in bot.muted_channels:
        bot.muted_channels.remove(channel.id)
        await interaction.response.send_message(f"Notifications enabled for {channel.mention}")
    else:
        bot.muted_channels.add(channel.id)
        await interaction.response.send_message(f"Notifications muted for {channel.mention}")

# Slash command to set a role for multiple users
@bot.tree.command(name="set_role", description="Assign role to multiple users")
@commands.has_permissions(manage_roles=True)
async def set_role(interaction: discord.Interaction, users_and_role: str):
    try:
        # Split users and role name
        users_str, role_name = users_and_role.split(';')
        users = [user.strip() for user in users_str.split()]
        role_name = role_name.strip()

        # Find role in server
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            await interaction.response.send_message(f"Role '{role_name}' not found.")
            return

        # Assign role to users
        success_count = 0
        for user_mention in users:
            user_id = int(user_mention.strip('<@!>'))
            member = interaction.guild.get_member(user_id)
            if member:
                await member.add_roles(role)
                success_count += 1

        await interaction.response.send_message(f"Assigned role {role.name} to {success_count}/{len(users)} users.")
    except ValueError:
        await interaction.response.send_message("Please enter the correct format: /set_role @user1 @user2 @user3 ; RoleName")
    except discord.Forbidden:
        await interaction.response.send_message("The bot doesn't have enough permissions to perform this action.")
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}")

# Slash command to check bot latency
@bot.tree.command(name="ping", description="Check bot's latency")
async def ping_command(interaction: discord.Interaction):
    latency = bot.latency * 1000
    await interaction.response.send_message(f'Bot latency is {latency:.2f}ms')

# Slash command to echo a user's message
@bot.tree.command(name="say", description="Echo the user's message")
async def say_command(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

# Slash command to clear messages in a channel
@bot.tree.command(name="clear", description="Clear messages in a channel")
@commands.has_permissions(manage_messages=True, administrator=True)
async def clear_command(interaction: discord.Interaction, limit: int):
    await interaction.channel.purge(limit=limit + 1)
    await interaction.response.send_message(f"Cleared {limit} messages.", ephemeral=True)

# Handle muted channels
@bot.event
async def on_message(message):
    if message.channel.id in bot.muted_channels:
        await message.channel.edit(default_auto_archive_duration=10080)  # Set to 7 days (10080 minutes)
    await bot.process_commands(message)

# Error handling for commands
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandNotFound):
        await interaction.response.send_message("Command not found. Please use /list to see available commands!")
    elif isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.")
    else:
        await interaction.response.send_message(f"An error occurred: {error}")
        logging.error(f"An error occurred: {error}")

# Run the bot
bot.run(TOKEN)

# run_bot.py
from bot import MyBot
import commands.commands as cmd_mod
import event.event as evt_mod
from config import TOKEN

bot = MyBot()

# Setup commands and events
cmd_mod.setup_commands(bot)
evt_mod.setup_events(bot)

bot.run(TOKEN)

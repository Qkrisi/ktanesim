try:
    from config import *
except:
    raise Exception("Copy config.template to config.py and edit the values!")

import discord
import FakeDiscord
import asyncio
import logging
import random
import leaderboard
import modules
import traceback
import BombSettings
from bomb import Bomb

async def cmd_help(channel, author, parts):
    print(f"Help: {channel}")
    await channel.send(f"This bot simulates Keep Talking and Nobody Explodes bombs. Message the bot in DMs for solo play or collaborate in text channels.\n"
        f"`{PREFIX}help --sim`: Show this message\n"
        f"`{PREFIX}bombs`: List the currently running bombs.\n"
        f"`{PREFIX}run ...`: Start a bomb. Pass no parameters for usage.\n"
        f"`{PREFIX}modules`: When a bomb is running, show the modules that have not been solved yet. When a bomb is not running, show a list of implemented modules.\n"
        f"`{PREFIX}unclaimed`: Shows {MAX_UNCLAIMED_LIST_SIZE} random unclaimed modules from the bomb.\n"
        f"`{PREFIX}find ...`: List all modules on the bomb with `...` in their name.\n"
        f"`{PREFIX}edgework`: Show the edgework string of the bomb.\n"
        f"`{PREFIX}status`: Show the bomb status.\n"
        f"`{PREFIX}<module number> view`: Show the module and link its manual.\n"
        f"`{PREFIX}<module number> claim`: Claim the module so that only you can give it commands.\n"
        f"`{PREFIX}<module number> unclaim`: Undo a `claim` command.\n"
        f"`{PREFIX}<module number> claimview`, alias `... cv`: `claim` and `view` combined.\n"
        f"`{PREFIX}<module number> player`: Show the player who claimed the module.\n"
        f"`{PREFIX}<module number> take`: If you think someone has abondoned the module, use this command to take it over.\n"
        f"`{PREFIX}claimany`: Claim a randomly chosen module, except for a Souvenir, Forget Me Not or Forget Everything.\n"
        f"`{PREFIX}claimanyview`, alias `{PREFIX}cvany`: `{PREFIX}claimany` and `view` combined.\n"
        f"`{PREFIX}claims`: Show the list of modules you have claimed.\n"
        f"`{PREFIX}detonate`: If other players agree, detonate the bomb.\n"
        f"`{PREFIX}leaderboard [<page number>]`, alias `{PREFIX}lb`: Show the leaderboard, {LEADERBOARD_PAGE_SIZE} items per page. Defaults to the first page.\n"
        f"`{PREFIX}rank`: Shows your leaderboard entry.\n"
        f"`{PREFIX}settings`: Shows information about bomb settings.\n"
        f"`{PREFIX}implement`: Shows information about implementing a module.\n"
        f"\n"
        f"Original KTaNE Simulator by NieDzejkob#2571, now maintained by Qkrisi#4982"
        )

async def cmd_invite(channel, author, parts):
    await channel.send("Here's one: https://discord.gg/gJVy2Rt")

async def cmd_implement(channel, author, parts):
    await channel.send(f"If you have some Python and SVG knowledge, feel free to submit a pull request to <https://github.com/Qkrisi/ktanesim> adding new modules.\n"
                       f"Setup help: <https://github.com/Qkrisi/ktanesim/blob/master/README.md>\n"
                       f"Documentation: <https://github.com/Qkrisi/ktanesim/wiki>\n"
                       f"If you need any help, join the KTaNE Bot server: <https://discord.gg/gJVy2Rt>")

async def cmd_allbombs(channel, author, parts):
    await channel.send(str(len(Bomb.bombs)))

logging.basicConfig(level=logging.INFO)
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
Bomb.client = client

UNICODE_TRANSLATION_TABLE = {ord(x): "'" for x in "`\u2018\u2019\u2032"}

@FakeDiscord.OnMessage
async def on_message(msg):
    print(f"Got message: {msg.content}")
    #if not isinstance(msg.channel, discord.channel.DMChannel) and msg.channel.id not in ALLOWED_CHANNELS: return
    if not msg.content.startswith(PREFIX): return

    parts = msg.content[len(PREFIX):].translate(UNICODE_TRANSLATION_TABLE).strip().split()
    try:command = parts.pop(0).lower()
    except:return
    channel = msg.channel
    author = msg.author

    try:
        GENERIC_COMMANDS = {
            "run": Bomb.cmd_run,
            "bombs": Bomb.cmd_bombs,
            "shutdown": Bomb.cmd_shutdown,
            "leaderboard": leaderboard.cmd_leaderboard,
            "lb": leaderboard.cmd_leaderboard,
            "rank": leaderboard.cmd_rank,
            "help": cmd_help,
            "invite": cmd_invite,
            "implement": cmd_implement,
            "allbombs": cmd_allbombs,
            "settings": BombSettings.cmd_settings
        }

        if command == "modules":
            if channel in Bomb.bombs:
                await Bomb.bombs[channel].cmd_modules(author, parts)
            else:
                await modules.cmd_modules(channel, author, parts)
        elif command in GENERIC_COMMANDS:
            await GENERIC_COMMANDS[command](channel, author, parts)
        elif command.isdigit() or command in Bomb.COMMANDS:
            if channel in Bomb.bombs:
                await Bomb.bombs[channel].handle_command(command, author, parts)
            else:
                await channel.send(f"{author.mention} No bomb is currently ticking in this channel. Change this sad fact with `{PREFIX}run`.")
        #else:
            #await channel.send(f"{author.mention} No such command: `{PREFIX}{command}`. Did you miss the module number? Try `{PREFIX}help` for help.")
    except Exception:
        await channel.send(f"{author.mention} An unidentified ~~flying object~~ error has occured during handling of this command. Please get the log for this bomb to one of our code monkeys, along with a description of what you did to cause this")
        print(f"Exception in {channel}:\n{traceback.format_exc()}")

FakeDiscord.Start()

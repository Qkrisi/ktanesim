import io
import os
import sys
import json
import time
import random
import asyncio
import aiohttp
import discord
import config
import modules
import edgework
import traceback
import BombSettings
from config import *

class Bomb:
    SERIAL_NUMBER_CHARACTERS = "ABCDEFGHIJKLMNEPQRSTUVWXZ0123456789"
    bombs = {}
    opc_session = None
    client = None
    shutdown_mode = False

    def __init__(self, channel, modules):
        self.channel = channel
        self.settings = BombSettings.get_settings(channel.id, True)
        self.strikes = 0
        self.start_time = time.monotonic()
        self.serial = self._randomize_serial()

        self.FileRoot = os.path.dirname(os.path.realpath(__file__))
        self.LogOut = f"{self.FileRoot}/logs"
        if not os.path.isdir(self.LogOut): os.mkdir(self.LogOut)

        self.edgework = []
        for _ in range(5):
            self.edgework.append(random.choice(edgework.WIDGETS)(self))

        self.modules = []
        random.shuffle(modules)
        for index, module in enumerate(modules):
            self.modules.append(module(self, index + 1))

    @property
    def strike_count(self):return self.strikes

    @property
    def starting_time(self):return self.start_time

    @property
    def serial_number(self):return self.serial

    @property
    def module_count(self):return len(self.modules)

    @staticmethod
    async def update_presence():
        return
        await Bomb.client.change_presence(activity=discord.Game(f"{len(Bomb.bombs)} bomb{'s' if len(Bomb.bombs) != 1 else ''}. {PREFIX}help for help"))

    @staticmethod
    async def cmd_shutdown(channel, author, parts):
        if parts:
            return await channel.send(f"{author.mention} Trailing arguments.")

        if author.id != BOT_OWNER:
            return await channel.send(f"{author.mention} You don't have permission to use this command.")

        Bomb.shutdown_mode = True

        for bomb_channel in Bomb.bombs:
            asyncio.ensure_future(bomb_channel.send(f"The bot is going into shutdown mode. No new bombs can be started and the bot will go offline when all currently running bombs are solved or detonated."))

        if not Bomb.bombs:
            await channel.send(f"***oof***")
            Bomb.client.loop.stop()
        else:
            await channel.send(f"{author.mention} Shutdown mode activated")

    @staticmethod
    async def cmd_bombs(channel, author, parts):
        if parts:
            return await channel.send(f"{author.mention} Trailing arguments.")

        if not Bomb.bombs:
            return await channel.send(f"{author.mention} No bombs are running.")

        response = f"{author.mention} Currently running bombs:"

        for bomb_channel, bomb in Bomb.bombs.items():
            response += f"\n- {bomb.get_solved_count()} out of {len(bomb.modules)} modules solved after {bomb.get_time_formatted()} and {bomb.strikes} {'strike' if bomb.strikes == 1 else 'strikes'} in {bomb_channel}"

        await channel.send(response)

    @staticmethod
    async def cmd_run(channel, author, parts):
        print(f"cmd_run: {author}: {channel}: {' '.join(parts)}")
        if channel in Bomb.bombs:
            return await channel.send(f"{author.mention} A bomb is already ticking in this channel! Solve that one first!")

        if Bomb.shutdown_mode:
            return await channel.send(f"{author.mention} The bot is in shutdown mode. No new bombs can be started.")

        usage = (
            f"{author.mention} Usage: `{PREFIX}run <module count> <module distributon> [-<module 1> [-<module 2> [...]]]` or "
            f"`{PREFIX}run <module 1>[*<count>] [<module 2>[*<count>] [...]]`.\n"
            f"For example:\n - `{PREFIX}run 7 vanilla` - 7 random vanilla modules\n"
            f" - `{PREFIX}run 12 mixed -password -switches` - 12 modules, half of them being vanilla. "
            f"Password and Switches modules will not be generated\n"
            f" - `{PREFIX}run keypad*3` - three Keypad modules and nothing else\n"
            f" - `{PREFIX}run complicatedWires morseCode hexamaze*2` - four modules: Complicated Wires, Morse Code, and two Hexamazes.\n"
            f"Use `{PREFIX}modules` to see the implemented modules.\nAvailable distributions:")

        distributions = {
            "vanilla": 1,
            "mods": 0,
            "modded": 0,
            "mixed": 0.5,
            "lightmixed": 0.67,
            "mixedlight": 0.67,
            "heavymixed": 0.33,
            "mixedheavy": 0.33,
            "light": 0.8,
            "heavy": 0.2,
            "extralight": 0.9,
            "extraheavy": 0.1
        }

        for distribution in distributions:
            if distribution not in ["lightmixed", "heavymixed", "modded"]:
                vanilla = int(distributions[distribution] * 100)
                usage += f"\n`{distribution}`: {vanilla}% vanilla, {100 - vanilla}% modded"

        if len(parts) < 1:
            return await channel.send(usage.format(author.mention, prefix=PREFIX))

        if parts[0].startswith('-') and parts[0][1:].isdigit():
            return await channel.send(f"{author.mention} A negative module count?! What does that mean? Antimatter?")

        if parts[0].isdigit():
            if len(parts) < 2 or parts[1].lower() not in distributions:
                return await channel.send(usage.format(author.mention, prefix=PREFIX))

            candidates_vanilla = modules.VANILLA_MODULES.copy()
            candidates_modded = modules.MODDED_MODULES.copy()
            module_count = int(parts[0])

            if module_count > 101:
                return await channel.send(f"{author.mention} Nope.")

            if module_count == 0:
                return await channel.send(f"{author.mention} A bomb with 0 modules has been... armed? Look, it doesn't seem to want to work. I don't think a bomb with no modules is a good idea.")

            for veto in parts[2:]:
                if not veto.startswith('-'):
                    return await channel.send(usage)

                veto = veto[1:]

                if veto in candidates_vanilla:
                    del candidates_vanilla[veto]
                elif veto in candidates_modded:
                    del candidates_modded[veto]
                else:
                    return await channel.send(f"{author.mention} No such module: `{veto}`")

            chosen_modules = []
            candidates_vanilla = list(candidates_vanilla.values())
            candidates_modded = list(candidates_modded.values())

            vanilla_count = int(distributions[parts[1].lower()] * module_count)

            if (not candidates_vanilla or vanilla_count == 0) and (not candidates_modded or vanilla_count == module_count):
                return await channel.send(f"{author.mention} You've blacklisted all the modules! If you don't want to play, just say so!")

            if not candidates_vanilla: vanilla_count = 0
            elif not candidates_modded: vanilla_count = module_count
            modded_count = module_count - vanilla_count

            for candidate_group, group_count in (candidates_vanilla, vanilla_count), (candidates_modded, modded_count):
                if candidate_group:
                    chosen_modules += candidate_group * (group_count // len(candidate_group))
                    chosen_modules += random.sample(candidate_group, group_count % len(candidate_group))
        else:
            chosen_modules = []
            candidates = {**modules.VANILLA_MODULES, **modules.MODDED_MODULES}
            for module in parts:
                if '*' in module:
                    if module.count('*') > 1:
                        return await channel.send(f"{author.mention} There are too many stars in `{module}`.")
                    left, right = module.split('*')
                    if left.isdigit() and not right.isdigit():
                        count = int(left)
                        module = right
                    elif not left.isdigit() and right.isdigit():
                        count = int(right)
                        module = left
                    else:
                        return await channel.send(f"{author.mention} `{module}`: which one is the module and which one is the count?")
                else:
                    count = 1
                if module not in candidates:
                    return await channel.send(f"{author.mention} No such module: `{module}`")

                if count > 101:
                    return await channel.send(f"{author.mention} Nope.")

                chosen_modules.extend([candidates[module]] * count)

                if len(chosen_modules) > 101:
                    return await channel.send(f"{author.mention} Nope.")

        bomb = Bomb(channel, chosen_modules)
        Bomb.bombs[channel] = bomb
        await channel.send(f"A bomb with {len(bomb.modules)} {'modules' if len(bomb.modules) != 1 else 'module'} has been armed!\nEdgework: `{bomb.get_edgework()}`")
        await Bomb.update_presence()

    async def bomb_end(self, boom=False):
        if Bomb.opc_session is None and config.USE_OPC:
            Bomb.opc_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=OPC_TIMEOUT))

        send_first_message_coro = asyncio.ensure_future(self.channel.send(f"{':boom:' if boom else ''} The bomb has been {'**detonated**' if boom else 'defused'} after {self.get_time_formatted()} and {self.strikes} strike{'s' if self.strikes != 1 else ''}."))

        discord_upload = True
        log = self.get_log()
        index = len(os.listdir(self.LogOut)) + 1
        filename = f"ktanesim_bomb{index}.log"
        if DEBUG_MODE:
            logurl = f"Debug mode enabled - uploading log to discord instead of OPC"
        elif config.USE_OPC:
            try:
                async with self.opc_session.post('https://api.onpointcoding.net/v2/logs', json={
                    "client_id": config.OPC_ID,
                    "client_secret": config.OPC_SECRET,
                    "log_data": log,
                    "log_format": "raw",
                    "log_filename": filename
                }) as resp:
                    decoded = json.loads(await resp.text())
                    if not decoded["error"]:
                        logurl = f"Log: https://logs.onpointcoding.net/file/{config.OPC_ID}/{decoded['log_id']}.log"
                        discord_upload = False
                    else:
                        error_message = "\n".join(decoded["error"])
                        print(f"OPC error: {error_message}")
                        logurl = f"OPC log upload failed with no error message, uploading to discord: ```\n{error_message}```"
            except asyncio.TimeoutError:
                logurl = f"OPC log upload failed with timeout, uploading to discord:"
            except Exception:
                logurl = f"OPC log upload failed with exception, uploading to discord:"

        if discord_upload:
            filepath = f"{self.LogOut}/{filename}"
            with open(filepath, "w") as file:file.write(log)
            file_ = {"path":filepath, "filename":filename}
        else:
            file_ = None

        await asyncio.gather(send_first_message_coro)
        await self.channel.send(logurl if config.USE_OPC else "", file=file_)
        del Bomb.bombs[self.channel]
        if Bomb.shutdown_mode and not Bomb.bombs:
            owner_user = discord.utils.find(lambda u: u.id == BOT_OWNER, Bomb.client.users)
            owner_dm = owner_user.dm_channel
            if owner_dm is None:
                owner_dm = await owner_user.create_dm()
            await owner_dm.send('Shutdown complete.')
            Bomb.client.loop.stop()
        else:
            await Bomb.update_presence()

    def get_log(self):
        log = ["Edgework: {:s}".format(self.get_edgework())]
        for module in self.modules:
            log.append(module.get_log())
        return '\n\n'.join(log)

    def FilterModules(self, func, output):
        return [output(module) for module in self.modules if func(module)]

    def get_claims(self, user):
        return self.FilterModules(lambda module: not module.solved and module.claim is not None and module.claim.id == user.id, lambda module: module)

    def get_module_names(self):
        return self.FilterModules(lambda module: True, lambda module: module.display_name)

    def get_solved_module_names(self):
        return self.FilterModules(lambda module: module.solved, lambda module: module.display_name)

    def get_widgets(self, type_):
        return list(filter(lambda widget: type(widget) is type_, self.edgework))

    def get_battery_count(self, filter = edgework.BatteryType.Any):
        assert isinstance(filter, edgework.BatteryType)
        return sum(widget.battery_count for widget in self.get_widgets(edgework.BatteryWidget) if filter.value==0 or widget.battery_count==filter.value)

    def get_holder_count(self):
        return len(self.get_widgets(edgework.BatteryWidget))

    def FilterIndicators(self, func):
        return [indicator for indicator in self.get_widgets(edgework.IndicatorWidget) if func(indicator)]

    def get_indicators(self):
        return self.FilterIndicators(lambda indicator: True)

    def get_lit_indicators(self):
        return self.FilterIndicators(lambda indicator: indicator.lit)

    def get_unlit_indicators(self):
        return self.FilterIndicators(lambda indicator: not indicator.lit)

    def get_indicator(self, code):
        assert isinstance(code, edgework.Indicator)
        for indicator in self.get_indicators():
            if indicator.code == code:
                return indicator.lit
        return None

    def get_port_plates(self):
        return self.get_widgets(edgework.PortPlateWidget)

    def get_plate_count(self):
        return len(self.get_port_plates())

    def get_ports(self):
        p = []
        for plate in self.get_port_plates():
            p+=[port.name for port in plate.ports]
        return p

    def port_count(self, port_type = None):
        assert port_type is None or isinstance(port_type, edgework.PortType)
        s = 0
        for plate in self.get_port_plates():
            s+=len(plate.ports) if port_type is None else plate.ports.count(port_type)
        return s

    def has_port(self, port_type):
        assert isinstance(port_type, edgework.PortType)
        return self.port_count(port_type) > 0

    def has_vowel(self):
        for vowel in "AEIOU":
            if vowel in self.serial:
                return True
        return False

    def get_edgework(self):
        widgets = [
            '{:d}B {:d}H'.format(self.get_battery_count(), self.get_holder_count()),
            ' '.join(map(str, self.get_widgets(edgework.IndicatorWidget))),
            ' '.join(map(str, self.get_widgets(edgework.PortPlateWidget))),
            self.serial]
        return ' // '.join(widget for widget in widgets if widget != '')

    def get_unclaimed(self):
        return [module for module in self.modules if module.claim is None and not module.solved]

    def get_claimed(self):
        return [module for module in self.modules if module.claim is not None and not module.solved]

    def get_time(self):
        return time.monotonic() - self.start_time

    def get_time_formatted(self):
        seconds = int(self.get_time())
        minutes = seconds // 60
        seconds %= 60
        hours = minutes // 60
        minutes %= 60
        return '{:d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

    def get_solved_count(self):
        return len(self.get_solved_module_names())

    def _randomize_serial(self):
        def get_any():
            return random.choice(Bomb.SERIAL_NUMBER_CHARACTERS)

        def get_letter():
            return random.choice(Bomb.SERIAL_NUMBER_CHARACTERS[:-10])

        def get_digit():
            return str(random.randint(0, 9))

        return get_any() + get_any() + get_digit() + get_letter() + get_letter() + get_digit()

    async def handle_command(self, command, author, parts):
        if command in Bomb.COMMANDS:
            await Bomb.COMMANDS[command](self, author, parts)
        elif command.isdigit():
            ident = int(command)
            if ident not in range(1, len(self.modules) + 1):
                await self.channel.send(f"{author.mention} Double check the module number - there {'are' if len(self.modules) != 1 else 'is'} only {len(self.modules)} {'modules' if len(self.modules) != 1 else 'module'} on this bomb!")
            elif not parts:
                await self.channel.send(f"{author.mention} What should I do with module {ident}? You need to give me a command!")
            else:
                command = parts.pop(0).lower()
                await self.modules[ident - 1].handle_command(command, author, parts)

    async def cmd_edgework(self, author, parts):
        if parts:
            return await self.channel.send(f"{author.mention} Trailing arguments.")

        await self.channel.send(f"{author.mention} Edgework: `{self.get_edgework()}`")

    async def cmd_unclaimed(self, author, parts):
        if parts:
            return await self.channel.send(f"{author.mention} Trailing arguments.")

        unclaimed = self.get_unclaimed()

        if unclaimed:
            if len(unclaimed) > MAX_UNCLAIMED_LIST_SIZE:
                reply = f'{MAX_UNCLAIMED_LIST_SIZE} randomly chosen unclaimed modules:'
                unclaimed = random.sample(unclaimed, MAX_UNCLAIMED_LIST_SIZE)
                unclaimed.sort(key=lambda module: module.ident)
            else:
                reply = 'Unclaimed modules:'

            for module in unclaimed:
                reply += f"\n#{module.ident}: {module.display_name}"
        else:
            reply = "There are no unclaimed modules."

        await self.channel.send(reply)

    async def cmd_modules(self, author, parts):
        if parts:
            return await self.channel.send(f"{author.mention} Trailing arguments.")

        claimed = self.get_claimed()
        if not claimed:
            return await self.cmd_unclaimed(author, parts)

        reply = f'Here are the modules that have currently been claimed by someone. Check `{PREFIX}unclaimed` for unclaimed modules:'

        if len(claimed) > MAX_CLAIMED_LIST_SIZE:
            claimed = random.sample(claimed, MAX_CLAIMED_LIST_SIZE)
            claimed.sort(key=lambda module: module.ident)

        for module in claimed:
            reply += f"\n{module} - claimed by {module.claim}"

        await self.channel.send(reply)

    async def cmd_claims(self, author, parts):
        if parts:
            return await self.channel.send(f"{author.mention} Trailing arguments.")

        claims = list(map(str, self.get_claims(author)))
        if len(claims) == 0:
            await self.channel.send(f"{author.mention} You have not claimed any modules.")
        elif len(claims) == 1:
            await self.channel.send(f"{author.mention} You have only claimed {claims[0]}.")
        else:
            await self.channel.send(f"{author.mention} You have claimed {', '.join(claims[::-1])} and {claims[-1]}.")

    async def cmd_status(self, author, parts):
        if parts:
            return await self.channel.send(f"{author.mention} Trailing arguments.")

        await self.channel.send(
            f"Zen mode on, time: {self.get_time_formatted()}, {self.strikes} strikes, "
            f"{self.get_solved_count()} out of {len(self.modules)} modules solved.")

    async def run_command_on_unclaimed(self, author, parts, command):
        unclaimed = [module for module in self.modules if not module.solved and module.claim is None]
        if not unclaimed:
            return await self.channel.send(f"{author.mention} Sorry, there are no unclaimed modules.")
        module = random.choice([module for module in self.modules if not module.solved and module.claim is None])
        await module.handle_command(command, author, parts)

    async def cmd_claimany(self, author, parts):
        await self.run_command_on_unclaimed(author, parts, "claim")

    async def cmd_claimanyview(self, author, parts):
        await self.run_command_on_unclaimed(author, parts, "claimview")

    async def cmd_detonate(self, author, parts):
        return await self.bomb_end(True)

    async def cmd_find(self, author, parts):
        if not parts:
            return await self.channel.send(f"{author.mention} What should I look for?")

        needle = ' '.join(parts).lower()
        found = []
        for module in self.modules:
            if needle in module.display_name.lower():
                found.append(module)
        if not found:
            return await self.channel.send(f"{author.mention} Sorry, I couldn't find anything.")
        else:
            trunc = False
            if len(found) > MAX_FOUND_LIST_SIZE:
                found = [module for module in found if not module.solved]

                if len(found) > MAX_FOUND_LIST_SIZE:
                    found = random.sample(found, MAX_FOUND_LIST_SIZE)
                    found.sort(key=lambda module: module.ident)
                    trunc = True

            found_str = [f"{module} - {module.get_status()}" for module in found]

            if len(found_str) == 1:
                await self.channel.send(f"{author.mention} I could only find {found_str[0]}")
            elif not trunc:
                await self.channel.send(f"{author.mention} Here's what I could find:\n" + '\n'.join(found_str))
            else:
                await self.channel.send(f"{author.mention} I've found a lot, so here are {MAX_FOUND_LIST_SIZE} randomly chosen modules:\n" + '\n'.join(found_str))

    COMMANDS = {
        "edgework": cmd_edgework,
        "status": cmd_status,
        "unclaimed": cmd_unclaimed,
        "modules": cmd_modules,
        "find": cmd_find,
        "claims": cmd_claims,
        "claimany": cmd_claimany,
        "claimanyview": cmd_claimanyview,
        "cvany": cmd_claimanyview,
        "detonate": cmd_detonate,
    }

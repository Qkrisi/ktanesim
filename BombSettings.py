import copy
import enum
import inspect
from config import PREFIX

ChannelSettings = {}


class Mode(enum.Enum):
    Normal = enum.auto()
    Zen = enum.auto()

    def __str__(self):
        return self.name


class BombSetting:
    def __init__(self, mode: Mode):
        self.mode = mode


DEFAULT_SETTINGS = BombSetting(Mode.Normal)


def get_handler(name: str, t: type):
    if issubclass(t, enum.Enum):
        available = [e.name for e in t]

        async def change_settings_enum(settings: BombSetting, value: str, channel):
            l = list(value.lower())
            l[0] = l[0].upper()
            value = "".join(l)
            if value not in available:
                return await channel.send(f'Invalid value! Available values: `{"`, `".join(available)}`')
            setattr(settings, name, getattr(t, value))
            await channel.send("Value changed successfully!")
        return [tuple(available), change_settings_enum]
    return [(), lambda settings, value, channel: None]


argspec = inspect.getfullargspec(BombSetting.__init__)
arguments = argspec.args[1:]

argument_cache = {arg: get_handler(arg, argspec.annotations[arg]) for arg in arguments}

help_message = (f'Usage:\n'
            f'`{PREFIX}settings set <setting name> <value>`\n'
            f'`{PREFIX}settings get <setting name>`\n'
            f'Available values: `{"`, `".join(arguments)}`',
                f'To see available values, run `{PREFIX}settings set <setting name>`')


def get_settings(channel_id: str, copy_settings: bool) -> BombSetting:
    if channel_id not in ChannelSettings:
        ChannelSettings[channel_id] = copy.deepcopy(DEFAULT_SETTINGS)
    value = ChannelSettings[channel_id]
    return value if not copy_settings else copy.deepcopy(value)


async def cmd_settings(channel, author, parts):
    if len(parts) == 0:
        return await channel.send(help_message)
    settings = get_settings(channel.id, False)
    state = parts[0].lower()
    if state == "get":
        if len(parts) < 2 or not hasattr(settings, parts[1]):
            return await channel.send(help_message)
        return await channel.send(f"Current value of `{parts[1]}`: `{str(getattr(settings, parts[1]))}`")
    elif state == "set":
        if len(parts) < 2 or not hasattr(settings, parts[1]):
            return await channel.send(help_message)
        handler = argument_cache[parts[1]]
        if len(parts) < 3:
            return await channel.send(f'Available values: `{"`, `".join(handler[0])}`')
        await handler[1](settings, parts[2], channel)
    else:
        return await channel.send(help_message)

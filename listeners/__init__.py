from datetime import datetime

from colorama import Fore

from discord import Embed
from discord.ext.commands import AutoShardedBot, Cog
from discord.ext.commands import (
    CommandOnCooldown,
    CommandNotFound,
    MissingRole,
    MissingPermissions,
    MissingRequiredArgument,
)


class Listeners(Cog):
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @Cog.listener(name="on_ready")
    async def on_ready(self):
        print(f"{Fore.YELLOW}Logged in as {self.bot.user}")

    @Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx, error):
        print(error)
        errors = (
            CommandOnCooldown,
            CommandNotFound,
            MissingRole,
            MissingPermissions,
            MissingRequiredArgument
        )

        def get_embed(err: str):
            return Embed.from_dict({
                "title": "Error!",
                "description": err,
                "timestamp": datetime.utcnow().isoformat(),
                "color": 16711379
            })

        if "Missing Permissions" in str(error):
            await ctx.send(embed=get_embed("Missing Permissions"))
        elif type(error) in errors:
            await ctx.send(embed=get_embed(error))

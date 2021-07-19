import os
import json
from time import time
from datetime import datetime

from discord.ext import commands
from discord import Embed, Member, TextChannel
from discord.ext.commands import AutoShardedBot


class Commands(commands.Cog):
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot
        self.description = "List of all the commands.\n.help commands"

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="help", brief="Helps with finding or using commands", usage=".help <command(optional)>")
    async def help(self, ctx, command: str = None):
        embed = {
            "title": "Commands",
            "description": "A list of all the commands.",
            "fields": [],
            "timestamp": datetime.utcnow().isoformat(),
            "color": 16711379
        }

        if command is None:
            for cmd in self.bot.commands:
                embed["fields"].append({
                    "name": f".{cmd.name}",
                    "value": f"{cmd.brief}\n```{cmd.usage}```"
                })
        else:
            try:
                cmd = self.bot.get_command(command.lower())
            except Exception:
                await ctx.send(embed=Embed.from_dict({
                    "title": "Error!",
                    "description": "Command not found.",
                    "timestamp": datetime.utcnow().isoformat(),
                    "color": 16711379
                }))
                return

            embed["fields"].append({
                "name": f".{cmd.name}",
                "value": f"{cmd.brief}\n```{cmd.usage}```"
            })

        await ctx.send(embed=Embed.from_dict(embed))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="ping", brief="Shows bot latency", usage=".ping")
    async def ping(self, ctx):
        now = time()
        embed = {
            "title": "Pong!",
            "timestamp": datetime.utcnow().isoformat(),
            "color": 16711379
        }
        message = await ctx.send(embed=Embed.from_dict(embed))
        embed["description"] = f"Latency: `{int((time() - now) * 1000)}ms`"
        await message.edit(embed=Embed.from_dict(embed))

    @commands.has_guild_permissions(ban_members=True)
    @commands.command(name="ban", brief="Bans a user", usage=".ban <member> <reason(optional)>")
    async def ban(self, ctx, member: Member, *args):
        await member.ban(reason=None if len(args) == 0 else " ".join(args))
        await ctx.send(embed=Embed.from_dict({
            "title": f"Banned {member}!",
            "description": f"Reason: {'N/A' if len(args) == 0 else ' '.join(args)}",
            "timestamp": datetime.utcnow().isoformat(),
            "color": 16711379
        }))

    @commands.has_guild_permissions(kick_members=True)
    @commands.command(name="kick", brief="Kicks a user", usage=".kick <member> <reason(optional)>")
    async def kick(self, ctx, member: Member = None, *args):
        await member.kick(reason=None if len(args) == 0 else " ".join(args))
        await ctx.send(embed=Embed.from_dict({
            "title": f"Kicked {member}!",
            "description": f"Reason: {'N/A' if len(args) == 0 else ' '.join(args)}",
            "timestamp": datetime.utcnow().isoformat(),
            "color": 16711379
        }))

    @commands.has_guild_permissions(administrator=True)
    @commands.command(name="nuke", brief="Nukes a channel", usage=".nuke <channel(optional)>")
    async def nuke(self, ctx, channel: TextChannel = None):
        channel = ctx.channel if channel is None else channel
        await channel.delete()
        new_channel = await channel.clone()
        await new_channel.edit(position=channel.position)
        await new_channel.send(embed=Embed.from_dict({
            "title": f"Nuked!",
            "description": f"This channel has been nuked.",
            "timestamp": datetime.utcnow().isoformat(),
            "color": 16711379
        }))

    @commands.has_guild_permissions(administrator=True)
    @commands.command(name="embed", brief="Sends an embed", usage=".embed <title> <content>")
    async def embed(self, ctx, title: str, *args):
        await ctx.send(embed=Embed.from_dict({
            "title": title,
            "description": " ".join(args),
            "timestamp": datetime.utcnow().isoformat(),
            "color": 16711379
        }))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="order", brief="Creates an order", usage=".order <description(optional)>")
    async def order(self, ctx, *args):
        if os.path.exists("orders.json") is False:
            open("orders.json", "w", encoding="utf-8").write("{}")

        orders = json.loads(open("orders.json").read())

        if str(ctx.author.id) in orders:
            await ctx.send(embed=Embed.from_dict({
                "title": f"Error!",
                "description": f"You already have an active order.",
                "timestamp": datetime.utcnow().isoformat(),
                "color": 16711379
            }))
            return

        channel = await ctx.guild.create_text_channel(f"order-{ctx.author.name}{ctx.author.discriminator}")

        orders[ctx.author.id] = channel.id
        open("orders.json", "w", encoding="utf-8").write(json.dumps(orders))

        await channel.set_permissions(ctx.guild.default_role, view_channel=False)

        for role in (ctx.author, ctx.guild.get_role(866778602611540058)):
            await channel.set_permissions(
                role,
                send_messages=True,
                read_messages=True,
                add_reactions=True,
                embed_links=True,
                attach_files=True,
                read_message_history=True,
                external_emojis=True
            )

        await channel.send(embed=Embed.from_dict({
            "title": f"Order - {ctx.author}",
            "description": f"Description: {'N/A' if len(args) == 0 else ' '.join(args)}",
            "timestamp": datetime.utcnow().isoformat(),
            "color": 16711379
        }))

        await ctx.send(embed=Embed.from_dict({
            "title": f"Order Created!",
            "description": f"<#{channel.id}>",
            "timestamp": datetime.utcnow().isoformat(),
            "color": 16711379
        }))

    @commands.has_guild_permissions(administrator=True)
    @commands.command(name="close", brief="Closes a ticket", usage=".close")
    async def close(self, ctx):
        orders = json.loads(open("orders.json", encoding="utf-8").read())

        for key, value in orders.copy().items():
            if ctx.channel.id == value:
                del orders[key]

        await ctx.channel.delete()

        open("orders.json", "w", encoding="utf-8").write(json.dumps(orders))


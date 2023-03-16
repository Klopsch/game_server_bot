import discord
from discord.ext import commands
from discord.ext.commands import Context

import cloud.gcloud
from cogs import ProjectID
from helpers import checks


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help", description="List all commands the bot has loaded."
    )
    @checks.not_blacklisted()
    async def help(self, context: Context) -> None:
        prefix = self.bot.config["prefix"]
        embed = discord.Embed(
            title="Help", description="List of available commands:", color=0x9C84EF
        )
        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()
            data = []
            for command in commands:
                description = command.description.partition("\n")[0]
                data.append(f"{prefix}{command.name} - {description}")
            help_text = "\n".join(data)
            embed.add_field(
                name=i.capitalize(), value=f"```{help_text}```", inline=False
            )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is alive.",
    )
    @checks.not_blacklisted()
    async def ping(self, context: Context) -> None:
        """
        Check if the bot is alive.
        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0x9C84EF,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="status",
        description="Get the status of all servers.",
    )
    @checks.not_blacklisted()
    async def status(self, context: Context) -> None:
        instances = cloud.gcloud.list_all_instances(ProjectID)
        for zone in instances:
            for i in instances[zone]:
                if "-bot-" not in i.name:
                    name = i.name.split("-")[0]
                    color = 0xFFFF00
                    if i.status == "RUNNING":
                        color = 0x00FF00
                    elif i.status == "TERMINATED":
                        color = 0xFF0000
                    embed = discord.Embed(
                        title=name,
                        description=f"Status: {i.status}",
                        color=color,
                    )
                    await context.send(embed=embed)

    @commands.hybrid_command(
        name="start",
        description="Start the server with the given name.",
    )
    @checks.not_blacklisted()
    async def start(self, context: Context, question: str) -> None:
        instances = cloud.gcloud.list_all_instances(ProjectID)
        for zone in instances:
            for i in instances[zone]:
                name = i.name.lower().split("-")[0]
                if question.lower() == name:
                    if i.status == "RUNNING":
                        embed = discord.Embed(
                            title=f"{name} server is already running.",
                            description="",
                            color=0x00FF00,
                        )
                        await context.send(embed=embed)
                    elif i.status == "TERMINATED":
                        embed = discord.Embed(
                            title=f"Starting {name} server.",
                            description="It may take a minute before the server is joinable.",
                            color=0x00FF00,
                        )
                        await context.send(embed=embed)
                        cloud.gcloud.start_instance(ProjectID, i.zone, i.name)
                    else:
                        embed = discord.Embed(
                            title=f"Cannot start {name}.",
                            description=f"Server {name} status is: {i.status}",
                            color=0xFF0000,
                        )
                        await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))

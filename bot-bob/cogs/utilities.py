from discord.ext import commands
from discord import app_commands, Interaction

import constants
import tagged
from logger import Logger


class Utilities(commands.Cog, tagged.Tagged):
    def __init__(self, bot):
        self.bot = bot
        self.TAG = type(self).__name__

    @app_commands.command(
        name="hi",
        description="hi",
    )
    async def hi(self, interaction: Interaction):
        Logger.v(self, f"got hi from {interaction.user}")
        await interaction.response.send_message("hi!")

    async def cog_command_error(self, ctx, error):
        Logger.e(self, f"{error}")


async def setup(bot):
    await bot.add_cog(Utilities(bot))

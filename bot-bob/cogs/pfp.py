from discord.ext import commands
from discord import app_commands, Interaction, Member
from dotenv import dotenv_values
import requests

import constants
import tagged
from logger import Logger
from main import GenericError
from util import Util


class Pfp(commands.GroupCog, tagged.Tagged):
    def __init__(self, bot):
        self.bot = bot
        self.TAG = type(self).__name__
        bob_string = [bob for bob in dotenv_values(constants.CONFIG_FILE)[constants.BOB_KEY].split('\n')][0]
        self.bob_id = int(bob_string.split(":")[0])

    @app_commands.command(
        name="me",
        description="updates bobot's pfp to yours"
    )
    async def me(self, interaction: Interaction):
        await self.__update_pfp_to_member(interaction, interaction.user)

    @me.error
    async def me_error(self, interaction: Interaction, error):
        Logger.e(GenericError(), Util.format_error(error))
        await Pfp.__error_pfp_update(interaction)

    @app_commands.command(
        name="you",
        description="updates bobot's pfp to someone else's"
    )
    async def you(self, interaction: Interaction, mention: Member):
        await self.__update_pfp_to_member(interaction, mention)

    @you.error
    async def you_error(self, interaction: Interaction, error):
        Logger.e(GenericError(), Util.format_error(error))
        await Pfp.__error_pfp_update(interaction)

    @app_commands.command(
        name="bob",
        description="updates bobot's pfp to bob's"
    )
    async def bob(self, interaction: Interaction):
        bob_member = next(
            filter(lambda member: member.id == self.bob_id, interaction.guild.members),
            None
        )

        if bob_member is None:
            await Pfp.__error_pfp_update(interaction)
        else:
            await self.__update_pfp_to_member(interaction, bob_member)

    @bob.error
    async def bob_error(self, interaction: Interaction, error):
        Logger.e(GenericError(), Util.format_error(error))
        await Pfp.__error_pfp_update(interaction)

    async def __update_pfp_to_member(self, interaction: Interaction, member: Member):
        avatar_url = member.avatar.url
        avatar_bytes = requests.get(avatar_url).content
        await self.bot.user.edit(avatar=avatar_bytes)

        if not interaction.response.is_done():
            await interaction.response.send_message(f"updated my pfp to {member.display_name}'s")

    @staticmethod
    async def __error_pfp_update(interaction: Interaction):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                content="couldn't copy pfp :(",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Pfp(bot))

from typing import Optional
from dotenv import dotenv_values
from discord.ext import commands
from discord import app_commands, Interaction, Member

import constants
import tagged
from util import Util
from logger import Logger


def check_if_not_bob(interaction: Interaction):
    return interaction.user.id != int(dotenv_values(constants.CONFIG_FILE)[constants.BOB_KEY])

class Bob(commands.GroupCog, tagged.Tagged):
    def __init__(self, bot):
        self.bot = bot
        self.TAG = type(self).__name__
        self.froggy_id = int(dotenv_values(constants.CONFIG_FILE)[constants.FROGGY_KEY])
        self.bob_id = int(dotenv_values(constants.CONFIG_FILE)[constants.BOB_KEY])

    @app_commands.command(
        name="mute",
        description="mutes bob",
    )
    @app_commands.check(check_if_not_bob)
    async def mute(self, interaction: Interaction):
        bob = await self.__check_bob_in_voice(self.__mute)

        message = "muted bob" if bob is not None and bob.voice.mute else "unmuted bob"

        await Bob.__message_if_bob_on(interaction, bob is not None, message)

    @mute.error
    async def mute_error(self, interaction: Interaction, error):
        await self.__handle_error(interaction, error)

    @staticmethod
    async def __mute(member: Member):
        await member.edit(mute=not member.voice.mute)

    @app_commands.command(
        name="deafen",
        description="deafens bob",
    )
    @app_commands.check(check_if_not_bob)
    async def deafen(self, interaction: Interaction):
        bob = await self.__check_bob_in_voice(self.__deafen)

        message = "deafened bob" if bob is not None and bob.voice.deaf else "undeafened bob"

        await Bob.__message_if_bob_on(interaction, bob is not None, message)

    @deafen.error
    async def deafen_error(self, interaction: Interaction, error):
        await self.__handle_error(interaction, error)

    @staticmethod
    async def __deafen(member: Member):
        await member.edit(deafen=not member.voice.deaf)

    @app_commands.command(
        name="disconnect",
        description="disconnects bob",
    )
    async def disconnect(self, interaction: Interaction):
        bob = await self.__check_bob_in_voice(self.__disconnect)

        await Bob.__message_if_bob_on(interaction, bob is not None, "disconnected bob")

    @staticmethod
    async def __disconnect(member: Member):
        await member.edit(voice_channel=None)

    @app_commands.command(
        name="kick",
        description="kicks bob",
    )
    @app_commands.describe(
        reason="reason for kicking bob",
    )
    async def kick(self, interaction: Interaction, reason: Optional[str]):
        guild_members = self.bot.get_guild(self.froggy_id).members
        bob_in_guild = False

        for member in guild_members:
            if member.id == self.bob_id:
                bob_in_guild = True
                await member.kick(reason=reason)

        if bob_in_guild:
            await interaction.response.send_message("kicked bob")
        else:
            await interaction.response.send_message("bob isn't even here")

    async def __handle_error(self, interaction: Interaction, error):
        if isinstance(error, app_commands.CheckFailure):
            await self.__error_bob(interaction)
        else:
            await self.__error(interaction)

    @staticmethod
    async def __message_if_bob_on(interaction: Interaction, is_bob_on: bool, message: str):
        if is_bob_on:
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message("bob isn't on")

    @staticmethod
    async def __error_bob(interaction: Interaction):
        await interaction.response.send_message(content="nice try bob")

    @staticmethod
    async def __error(interaction: Interaction):
        await interaction.response.send_message(
            content=constants.GENERIC_ERROR,
            ephemeral=True
        )

    async def __check_bob_in_voice(self, do_if_bob):
        voice_channels = self.bot.get_guild(self.froggy_id).voice_channels

        for voice_channel in voice_channels:
            for member in voice_channel.members:
                if member.id == self.bob_id:
                    await do_if_bob(member)
                    return member

        return None

    async def cog_command_error(self, ctx, error):
        Logger.e(self, f"{error}")


async def setup(bot):
    await bot.add_cog(Bob(bot))
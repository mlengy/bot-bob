from typing import Optional
from discord.ext import commands
from discord import app_commands, Interaction, Member

import constants
import tagged
from logger import Logger
from main import GenericError
from util import get_bobs, check_if_not_bob, format_error


class Bob(commands.GroupCog, tagged.Tagged):
    def __init__(self, bot):
        self.bot = bot
        self.TAG = type(self).__name__
        self.bob_ids = get_bobs()

    @app_commands.command(
        name="mute",
        description="mutes bob",
    )
    @app_commands.check(check_if_not_bob)
    async def mute(self, interaction: Interaction):
        bobs = await self.__get_bobs_in_voice(interaction)
        changed_bobs = []

        at_least_one_bob_unmuted = await Bob.__at_least_one_bob(bobs, lambda b: b.voice.mute)

        for bob in bobs:
            if bob.voice.mute != at_least_one_bob_unmuted:
                changed_bobs.append(self.bob_ids[bob.id])

            await Bob.__mute(bob, at_least_one_bob_unmuted)

        action = "muted" if at_least_one_bob_unmuted else "unmuted"
        message = "\n".join([f"{action} {changed_bob}" for changed_bob in changed_bobs])

        await Bob.__message_if_bob_on(interaction, len(bobs) > 0, message)

    @mute.error
    async def mute_error(self, interaction: Interaction, error):
        Logger.e(GenericError(), format_error(error))
        await self.__handle_error(interaction, error)

    @staticmethod
    async def __mute(member: Member, mute: bool):
        await member.edit(mute=mute)

    @app_commands.command(
        name="deafen",
        description="deafens bob",
    )
    @app_commands.check(check_if_not_bob)
    async def deafen(self, interaction: Interaction):
        bobs = await self.__get_bobs_in_voice(interaction)
        changed_bobs = []

        at_least_one_bob_undeafened = await Bob.__at_least_one_bob(bobs, lambda b: b.voice.deaf)

        for bob in bobs:
            if bob.voice.deaf != at_least_one_bob_undeafened:
                changed_bobs.append(self.bob_ids[bob.id])

            await Bob.__deafen(bob, at_least_one_bob_undeafened)

        action = "deafened" if at_least_one_bob_undeafened else "undeafened"
        message = "\n".join([f"{action} {changed_bob}" for changed_bob in changed_bobs])

        await Bob.__message_if_bob_on(interaction, len(bobs) > 0, message)

    @deafen.error
    async def deafen_error(self, interaction: Interaction, error):
        Logger.e(GenericError(), format_error(error))
        await self.__handle_error(interaction, error)

    @staticmethod
    async def __deafen(member: Member, deafen: bool):
        await member.edit(deafen=deafen)

    @app_commands.command(
        name="disconnect",
        description="disconnects bob",
    )
    async def disconnect(self, interaction: Interaction):
        bobs = await self.__get_bobs_in_voice(interaction)

        for bob in bobs:
            await Bob.__disconnect(bob)

        message = "\n".join([f"disconnected {self.bob_ids[bob.id]}" for bob in bobs])

        await Bob.__message_if_bob_on(interaction, len(bobs) > 0, message)

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
        guild_members = interaction.guild.members
        bobs_kicked = []

        for member in guild_members:
            if member.id in self.bob_ids:
                bobs_kicked.append(self.bob_ids[member.id])
                await member.kick(reason=reason)

        if bobs_kicked:
            message = "\n".join([f"kicked {bob_kicked}" for bob_kicked in bobs_kicked])
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message("bob isn't even here")

    async def __handle_error(self, interaction: Interaction, error):
        if not interaction.response.is_done():
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

    async def __get_bobs_in_voice(self, interaction: Interaction):
        voice_channels = interaction.guild.voice_channels
        bobs_in_voice = []

        for voice_channel in voice_channels:
            for member in voice_channel.members:
                if member.id in self.bob_ids:
                    bobs_in_voice.append(member)

        return bobs_in_voice

    @staticmethod
    async def __at_least_one_bob(bobs, condition):
        for bob in bobs:
            if not condition(bob):
                return True

        return False

    async def cog_command_error(self, ctx, error):
        Logger.e(self, f"{error}")


async def setup(bot):
    await bot.add_cog(Bob(bot))

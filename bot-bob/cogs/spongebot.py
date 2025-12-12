from discord.ext import commands
from discord import app_commands, Interaction, Message
from enum import Enum
import random
import re

import constants
import tagged
from logger import Logger

AUTO_ENABLED = False
# amount of messages needed before next spongebot is between
# AUTO_MESSAGE_OFFSET and AUTO_MESSAGE_OFFSET + AUTO_MESSAGE_RANGE inclusive on both sides
AUTO_MESSAGE_OFFSET = 100
AUTO_MESSAGE_RANGE = 50

MODIFIER_STRINGS = [
    "*",
    "**",
    "***"
]


class Spongebot(commands.Cog, tagged.Tagged):
    def __init__(self, bot):
        self.bot = bot
        self.TAG = type(self).__name__
        self.message_counter = 0
        self.__compute_new_message_limit()

        self.mock_context_menu = app_commands.ContextMenu(
            name='mock',
            callback=self.__mock_context_menu
        )
        self.bot.tree.add_command(self.mock_context_menu)

    @app_commands.command(
        name="mock",
        description="turns your message into a mocking message"
    )
    @app_commands.describe(
        message="a message to mock"
    )
    async def mock(self, interaction: Interaction, message: str):
        modified_text = Spongebot.__spongebob_mock(self, message)
        await self.__mock(interaction, modified_text)

    async def __mock_context_menu(self, interaction: Interaction, message: Message):
        modified_text = Spongebot.__spongebob_mock(self, message.clean_content)
        await self.__mock(interaction, modified_text)

    @staticmethod
    async def __mock(interaction: Interaction, message: str):
        if message is None:
            return

        member_name = interaction.user.display_name
        member_pfp_url = interaction.user.display_avatar.url

        webhook = await interaction.channel.create_webhook(name=member_name)

        await webhook.send(message, username=member_name, avatar_url=member_pfp_url)
        await webhook.delete()

        await interaction.response.send_message(
            content=random.choice(constants.MOCK_RESPONSES),
            ephemeral = True
        )

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author == self.bot.user:
            return

        text = message.clean_content

        if text.startswith(constants.PREFIX):
            return

        if self.message_counter < self.message_limit:
            self.message_counter += 1
            return
        else:
            self.message_counter = 0
            self.__compute_new_message_limit()

        modified_text = Spongebot.__spongebob_mock(self, text)

        if modified_text is not None:
            await message.reply(modified_text)

    @staticmethod
    def __spongebob_mock(spongebot, text):
        # remove custom emojis
        emoji_pattern = r'<:.*?:\d+?>'
        # remove existing modifiers, leading, and trailing whitespace
        clean_text = re.sub(emoji_pattern, '', text.replace('*', '')).strip()

        if len(clean_text) == 0:
            return None

        if clean_text.isspace():
            return None

        Logger.v(spongebot, f"spongebotting message: [\n{clean_text}\n]")

        # whether we are currently modifying characters, not modifying characters, or waiting for a gap
        modifier_status = Spongebot.ModifierStatus.NO_MODIFIER
        # previous modifier if we are currently modifying
        previous_modifier = Spongebot.Modifier.NONE
        # range in which to generate integers, including 0, excluding the value itself
        random_range = 6
        modified_text = ""

        for char in clean_text:
            modified_char = char

            # this random number determines what case we use and what modification behavior is applied
            determiner = random.randrange(random_range)

            # use each case around half the time
            if determiner % 2 == 0:
                modified_char = modified_char.lower().swapcase()

            # start modification of characters if all the following are true
            #     - we are not waiting for a gap or currently modifying
            #     - the next character is not whitespace
            #     - our random determiner allows us to modify the characters
            if modifier_status == Spongebot.ModifierStatus.NO_MODIFIER and not char.isspace() and determiner < len(
                    MODIFIER_STRINGS):
                # switch status to currently modifying
                modifier_status = Spongebot.ModifierStatus.YES_MODIFIER
                # store current modifier type
                previous_modifier = Spongebot.Modifier(determiner)
                # modify the character
                modified_char = f"{str(previous_modifier)}{modified_char}"
            # if we are currently modifying
            elif modifier_status == Spongebot.ModifierStatus.YES_MODIFIER:
                # finish modification of characters if any of the following are true
                #     - the next character is whitespace
                #     - our random determiner does not allow us to modify the characters
                #     - our determiner modifier type is different from our current modifier type
                if char.isspace() or determiner > len(MODIFIER_STRINGS) - 1 or previous_modifier != Spongebot.Modifier(
                        determiner):
                    # switch status to skip next character for modification
                    modifier_status = Spongebot.ModifierStatus.GAP_MODIFIER
                    # cap off modification and append next character
                    modified_char = f"{str(previous_modifier)}{modified_char}"
                    # reset current modifier type
                    previous_modifier = Spongebot.Modifier.NONE
                # continue modification of characters
                else:
                    pass
            # if we are waiting for a gap
            else:
                # stop waiting for the gap
                modifier_status = Spongebot.ModifierStatus.NO_MODIFIER

            modified_text += modified_char

        # if modification has not finished but the string is over
        if modifier_status == Spongebot.ModifierStatus.YES_MODIFIER:
            # cap off the modification
            modified_text += str(previous_modifier)

        Logger.v(spongebot, f"spongebotted message: [\n{modified_text}\n]")
        return modified_text

    def __compute_new_message_limit(self):
        self.message_limit = random.randrange(AUTO_MESSAGE_RANGE + 1) + AUTO_MESSAGE_OFFSET

    async def cog_command_error(self, ctx, error):
        Logger.e(self, f"{error}")

    class Modifier(Enum):
        NONE = -1
        ITALIC = 0
        BOLD = 1
        ITALIC_BOLD = 2

        def __str__(self):
            if self == Spongebot.Modifier.NONE:
                return ""
            else:
                return MODIFIER_STRINGS[self.value]

    class ModifierStatus(Enum):
        NO_MODIFIER = 0
        GAP_MODIFIER = 1
        YES_MODIFIER = 2


async def setup(bot):
    await bot.add_cog(Spongebot(bot))

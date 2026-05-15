from discord import Spotify, TextChannel
from dotenv import dotenv_values
from discord.ext import commands

import constants
import tagged
from logger import Logger
from main import GenericError
from util import format_error, is_admin


class D4VDetector(commands.Cog, tagged.Tagged):
    def __init__(self, bot):
        self.bot = bot
        self.TAG = type(self).__name__
        self.targets = [target for target in dotenv_values(constants.CONFIG_FILE)[constants.D4VD_TARGETS_KEY].split('\n')]
        self.channels = [int(channel) for channel in dotenv_values(constants.CONFIG_FILE)[constants.D4VD_CHANNELS_KEY].split('\n')]
        self.artists = [artist for artist in dotenv_values(constants.CONFIG_FILE)[constants.D4VD_ARTISTS_KEY].split('\n')]

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        # Logger.d(self, f"============================== {after.display_name}")

        spotify_before = next((activity.artist for activity in before.activities if isinstance(activity, Spotify)), "")
        spotify_after = next((activity.artist for activity in after.activities if isinstance(activity, Spotify)), "")

        if spotify_before == "":
            return

        channels = [self.bot.get_channel(int(channel)) for channel in self.channels]
        text_channels = [text_channel for text_channel in channels if isinstance(text_channel, TextChannel)]

        #604733336048631810

        # Logger.d(self, f"================== {after.display_name} LISTENING TO:")
        #
        # Logger.d(self, spotify_after)
        #
        # Logger.d(self, f"{text_channels}")

        if spotify_after != spotify_before:
            for artist in self.artists:
                # Logger.d(self, f"artist: {artist}, thing: {spotify_after.lower()}")
                # Logger.d(self, f"{artist in spotify_after.lower()}")
                if artist in spotify_after.lower():
                    # Logger.d(self, f"SEND!!")
                    for channel in text_channels:
                        await channel.send(f"‼️🚨📢 IMPORTANT PUBLIC SERVICE ANNOUNCEMENT!!! 📢🚨‼️\n\n{after.mention} IS LISTENING TO {spotify_after}!!!")

async def setup(bot):
    await bot.add_cog(D4VDetector(bot))

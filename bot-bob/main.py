import discord
from dotenv import dotenv_values
from discord.ext import commands

import constants
import tagged
from logger import Logger


COG_TYPE_ESSENTIALS = "essentials"
COG_TYPE_FUN = "fun"

ENABLED_COG_TYPES = {
    COG_TYPE_ESSENTIALS,
    COG_TYPE_FUN
}
COGS = {
    COG_TYPE_ESSENTIALS: [
        "utilities",
        "bob"
    ],
    COG_TYPE_FUN: [
        "spongebot"
    ]
}

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix=constants.PREFIX, intents=intents)

class Main(tagged.Tagged):
    def __init__(self):
        self.TAG = type(self).__name__

    @staticmethod
    async def setup_cogs():
        main = Main()
        Logger.i(main, "start cog setup")
        for cog_type in COGS:
            if cog_type in ENABLED_COG_TYPES:
                Logger.i(main, f"loading cogs in {cog_type}")
                for cog in COGS[cog_type]:
                    Logger.i(main, f"    loading cog {cog}")
                    await bot.load_extension(f"cogs.{cog}")
            else:
                Logger.i(main, f"skipping cogs in {cog_type}")
        Logger.i(main, "finish cog setup")

    @staticmethod
    async def bot_setup():
        Logger.i(Main(), "bot ready as {0.user}".format(bot))
        Logger.divider()
        await bot.change_presence(
            status=discord.Status.dnd,
            activity=discord.CustomActivity("watching bob")
        )

        await Main.setup_cogs()

    @staticmethod
    @bot.event
    async def on_ready():
        await Main.bot_setup()
        await bot.tree.sync()

    @staticmethod
    def main():
        if __name__ == "__main__":
            if not constants.PATH_TO_BOT:
                raise Exception("Bot path is missing!")

            token = dotenv_values(constants.ENV_TOKEN)[constants.TOKEN_KEY]
            bot.run(token)


Main.main()

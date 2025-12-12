import sys
from enum import Enum
from datetime import datetime, timezone

import tagged


class Logger:
    @staticmethod
    def v(tagged_object: tagged.Tagged, message):
        Logger.__log(Logger.Level.VERBOSE, tagged_object, message)

    @staticmethod
    def d(tagged_object: tagged.Tagged, message):
        Logger.__log(Logger.Level.DEBUG, tagged_object, message)

    @staticmethod
    def i(tagged_object: tagged.Tagged, message):
        Logger.__log(Logger.Level.INFO, tagged_object, message)

    @staticmethod
    def w(tagged_object: tagged.Tagged, message):
        Logger.__log(Logger.Level.WARN, tagged_object, message)

    @staticmethod
    def e(tagged_object: tagged.Tagged, message):
        Logger.__log(Logger.Level.ERROR, tagged_object, message)

    @staticmethod
    def divider():
        print("==================================================")

    @staticmethod
    def __log(level, tagged_object: tagged.Tagged, message):
        lines = message.splitlines()

        output_type = sys.stderr if level == Logger.Level.ERROR else sys.stdout
        date_time_string = datetime.now(timezone.utc).isoformat()

        for line in lines:
            message_formatted = f"{date_time_string} [{level.name}] {tagged_object.TAG}: {line}"
            print(message_formatted, file=output_type)

    class Level(Enum):
        VERBOSE = 00
        DEBUG = 10
        INFO = 20
        WARN = 30
        ERROR = 40
        CRITICAL = 50

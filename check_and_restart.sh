#!/bin/sh
if ! pgrep -f "bot-bob/main.py" > /dev/null
then
    /home/ubuntu/bot-gary/run_bot.sh &> /dev/null &
fi

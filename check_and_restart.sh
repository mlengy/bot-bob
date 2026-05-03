#!/bin/sh
if ! pgrep -f "bot-gary/main.py" > /dev/null
then
    /home/ubuntu/bot-gary/run_bot.sh &> /dev/null &
fi

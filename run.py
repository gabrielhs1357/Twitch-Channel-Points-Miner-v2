# -*- coding: utf-8 -*-
import logging
import os
from xmlrpc.client import Boolean

from colorama import Fore
from dotenv import load_dotenv

from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.Discord import Discord
from TwitchChannelPointsMiner.classes.entities.Bet import (
    BetSettings,
    Condition,
    DelayMode,
    FilterCondition,
    OutcomeKeys,
    Strategy,
)
from TwitchChannelPointsMiner.classes.entities.Streamer import (
    Streamer,
    StreamerSettings,
)
from TwitchChannelPointsMiner.classes.Matrix import Matrix
from TwitchChannelPointsMiner.classes.Pushover import Pushover
from TwitchChannelPointsMiner.classes.Settings import Events, FollowersOrder, Priority
from TwitchChannelPointsMiner.classes.Telegram import Telegram
from TwitchChannelPointsMiner.logger import ColorPalette, LoggerSettings

load_dotenv()

twitch_miner = TwitchChannelPointsMiner(
    username=os.getenv('USERNAME'),
    password=os.getenv('PASSWORD'),           # If no password will be provided, the script will ask interactively
    claim_drops_startup=False,                  # If you want to auto claim all drops from Twitch inventory on the startup
    priority=[                                  # Custom priority in this case for example:
        Priority.STREAK,                        # - We want first of all to catch all watch streak from all streamers
        Priority.DROPS,                         # - When we don't have anymore watch streak to catch, wait until all drops are collected over the streamers
        Priority.ORDER                          # - When we have all of the drops claimed and no watch-streak available, use the order priority (POINTS_ASCENDING, POINTS_DESCEDING)
    ],
    enable_analytics=True,                     # Disables Analytics if False. Disabling it significantly reduces memory consumption
    disable_ssl_cert_verification=False,        # Set to True at your own risk and only to fix SSL: CERTIFICATE_VERIFY_FAILED error
    disable_at_in_nickname=False,               # Set to True if you want to check for your nickname mentions in the chat even without @ sign
    logger_settings=LoggerSettings(
        save=False,                              # If you want to save logs in a file (suggested)
        console_level=logging.INFO,             # Level of logs - use logging.DEBUG for more info
        console_username=False,                 # Adds a username to every console log line if True. Useful when you have many open consoles with different accounts
        auto_clear=False,                        # Create a file rotation handler with interval = 1D and backupCount = 7 if True (default)
        time_zone="America/Sao_Paulo",                           # Set a specific time zone for console and file loggers. Use tz database names. Example: "America/Denver"
        file_level=logging.DEBUG,               # Level of logs - If you think the log file it's too big, use logging.INFO
        emoji=True,                             # On Windows, we have a problem printing emoji. Set to false if you have a problem
        less=True,                             # If you think that the logs are too verbose, set this to True
        colored=True,                           # If you want to print colored text
        color_palette=ColorPalette(             # You can also create a custom palette color (for the common message).
            STREAMER_online="GREEN",            # Don't worry about lower/upper case. The script will parse all the values.
            streamer_offline="red",             # Read more in README.md
            BET_wiN=Fore.MAGENTA                # Color allowed are: [BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET].
        ),
        telegram=None,
        discord=Discord(
            webhook_api=os.getenv('DISCORD_WEBHOOK') ,  # Discord Webhook URL
            events=[
                    Events.STREAMER_ONLINE,
                    Events.STREAMER_OFFLINE,
                    Events.GAIN_FOR_RAID, 
                    Events.GAIN_FOR_CLAIM,
                    Events.GAIN_FOR_WATCH,
                    Events.GAIN_FOR_WATCH_STREAK,
                    Events.BONUS_CLAIM,
                    Events.CHAT_MENTION
                ],                                  # Only these events will be sent to the chat
        ),
        matrix=None,
        pushover=None
    ),
    streamer_settings=StreamerSettings(
        make_predictions=False,                  # If you want to Bet / Make prediction
        follow_raid=True,                       # Follow raid to obtain more points
        claim_drops=True,                       # We can't filter rewards base on stream. Set to False for skip viewing counter increase and you will never obtain a drop reward from this script. Issue #21
        claim_moments=True,                     # If set to True, https://help.twitch.tv/s/article/moments will be claimed when available
        watch_streak=True,                      # If a streamer go online change the priority of streamers array and catch the watch screak. Issue #11
        chat=ChatPresence.ALWAYS,               # Join irc chat to increase watch-time [ALWAYS, NEVER, ONLINE, OFFLINE]
        bet=None
    )
)

streamers = os.getenv('CHANNELS').split(',')
    
analytics_enabled = bool(os.getenv('ANALYTICS_ENABLED'))

if analytics_enabled:
    twitch_miner.analytics(host="0.0.0.0", port=5000, refresh=5, days_ago=7)   # Start the Analytics web-server

twitch_miner.mine(
    streamers,                                  # Array of streamers (order = priority)
    followers=False,                    # Automatic download the list of your followers
    followers_order=FollowersOrder.ASC  # Sort the followers list by follow date. ASC or DESC
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater
from telegram.ext.dispatcher import run_async
from time import sleep
import os
import logging
import argparse
import configure
# Enable Logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

# We use this var to save the last chat id, so we can reply to it
last_chat_id = 0

def debugInfo(update):
    print update.message.text
    #print 'Incoming message'

def echo(bot, update, args):
    debugInfo(update)
    text_echo = ' '.join(args)
    bot.sendMessage(chat_id=update.message.chat_id, text=text_echo)

def any_message(bot, update):
    debugInfo(update)

    # Save last chat_id to use in reply handler
    global last_chat_id
    last_chat_id = update.message.chat_id

    logger.info("New message\nFrom: %s\nchat_id: %d\nText: %s" %
                (update.message.from_user,
                 update.message.chat_id,
                 update.message.text))


def unknown_command(bot, update):
    debugInfo(update)
    #bot.sendMessage(update.message.chat_id, text='请坐和放宽')

@run_async
def message(bot, update, **kwargs):
    bot.sendMessage(chat_id=last_chat_id, text='Got it')

# These handlers are for updates of type str. We use them to react to inputs
# on the command line interface
def cli_reply(bot, update, args):
    debugInfo(update)

    if last_chat_id is not 0:
        bot.sendMessage(chat_id=last_chat_id, text=' '.join(args))


def cli_noncommand(bot, update, update_queue):
    debugInfo(update)

    update_queue.put('/%s' % update)


def unknown_cli_command(bot, update):
    debugInfo(update)
    logger.warn("Command not found: %s" % update)


def error(bot, update, error):
    debugInfo(update)
    """ Print error to console """
    logger.warn('Update %s caused error %s' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's __bot_token__.

    updater = Updater(__bot_token__, workers=10)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # This is how we add handlers for Telegram messages
    # Message handlers only receive updates that don't contain commands
    dp.addTelegramMessageHandler(message)
    # Regex handlers will receive all updates on which their regex matches
    #dp.addTelegramRegexHandler('.*', any_message)

    # String handlers work pretty much the same
    dp.addStringCommandHandler('reply', cli_reply)
    #dp.addUnknownStringCommandHandler(unknown_cli_command)
    dp.addStringRegexHandler('[^/].*', cli_noncommand)

    # All TelegramErrors are caught for you and delivered to the error
    # handler(s). Other types of Errors are not caught.
    dp.addErrorHandler(error)

    # Start the Bot and store the update Queue, so we can insert updates
    update_queue = updater.start_polling(poll_interval=0.1, timeout=10)

    '''
    # Alternatively, run with webhook:
    updater.bot.setWebhook(webhook_url='https://example.com/%s' % __bot_token__,
                           certificate=open('cert.pem', 'rb'))
    update_queue = updater.start_webhook('0.0.0.0',
                                         443,
                                         url_path=__bot_token__,
                                         cert='cert.pem',
                                         key='key.key')
    # Or, if SSL is handled by a reverse proxy, the webhook URL is already set
    # and the reverse proxy is configured to deliver directly to port 6000:
    update_queue = updater.start_webhook('0.0.0.0',
                                         6000)
    '''

    # Start CLI-Loop
    while True:
        try:
            text = raw_input()
        except NameError:
            text = input()

        # Gracefully stop the event handler
        if text == 'stop':
            updater.stop()
            break

        # else, put the text into the update queue to be handled by our handlers
        elif len(text) > 0:
            update_queue.put(text)

if __name__ == '__main__':
    main()

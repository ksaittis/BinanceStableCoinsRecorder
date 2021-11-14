import logging
import os
from enum import Enum
from typing import List

import requests


class Emoji(Enum):
    GREEN_SQUARE = '\U0001F7E9'
    RED_SQUARE = '\U0001F7E5'
    FIRE = '\U0001F525'
    STAR = '\U00002B50'


class Message:
    value: str
    chat_id: str = None

    def __init__(self, value):
        self.chat_id = os.environ['CHAT_ID']
        self.value = value

    def text(self) -> str:
        return self.value


class MessageBuilder:

    @staticmethod
    def build_message(current_balance: float, diff: float) -> Message:
        prefix = Emoji.RED_SQUARE.value
        if diff >= 100:
            prefix = Emoji.FIRE.value
        elif diff >= 0:
            prefix = Emoji.GREEN_SQUARE.value

        return Message(f"{prefix} Balance: ${current_balance:.2f}, Change: ${diff:.2f}")


class TelegramMessenger:
    BASE_ENDPOINT = 'https://api.telegram.org/bot'

    def __init__(self):
        self.bot_token = os.environ['BOT_TOKEN']

    def send_message(self, message: Message):
        telegram_send_message_endpoint = self.build_message_endpoint(message)
        response = requests.get(telegram_send_message_endpoint)
        if response.ok:
            logging.info(f"Message delivery successful: {response.status_code} {message.value}")
        else:
            logging.warning(f"Message delivery unsuccessful: {response.status_code} {message.value}")

    def build_message_endpoint(self, message: Message) -> str:
        return f'https://api.telegram.org/bot{self.bot_token}/sendMessage?' \
               f'chat_id={message.chat_id}' \
               f'&parse_mode=Markdown' \
               f'&text={message.text()}' \
               f'&disable_web_page_preview=true'

    def send_messages(self, messages: List[Message]):
        for message in messages:
            self.send_message(message)


class MessageManager:
    def __init__(self):
        self.telegram_messenger = TelegramMessenger()
        self.message_builder = MessageBuilder()

    def build_message(self, current_balance, diff) -> Message:
        return self.message_builder.build_message(current_balance, diff)

    def send_message(self, message: Message):
        self.telegram_messenger.send_message(message)

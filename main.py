import logging
import os
from enum import Enum
from typing import List

import requests
from binance import Client
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class StableCoins:
    STABLE_COINS = ['BUSD', 'USDT', 'USDC']

    @staticmethod
    def get_stable_coins():
        return StableCoins.STABLE_COINS


class BinanceClient:

    def __init__(self):
        self.client = Client(os.environ['API_KEY'], os.environ['API_SECRET'])

    def get_balance(self, asset: str) -> dict:
        return self.client.get_asset_balance(asset=asset)

    def get_locked_balance(self, asset: str) -> str:
        return self.get_balance(asset)['locked']

    def get_free_balance(self, asset: str) -> str:
        return self.get_balance(asset)['free']

    def get_total_stable_coins_balance(self) -> float:
        total_balance: float = 0
        for stable_coin in StableCoins.get_stable_coins():
            total_balance += float(self.get_free_balance(stable_coin))
        return total_balance


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


class BalanceDB:
    @staticmethod
    def store_balance(value: float):
        with open('last_balance.txt', 'w') as f:
            f.write(str(value))

    @staticmethod
    def get_balance() -> float:
        try:
            with open('last_balance.txt', 'r') as f:
                return float(f.read().rstrip())
        except FileNotFoundError:
            return 0


class Emoji(Enum):
    GREEN_SQUARE = '\U0001F7E9'
    RED_SQUARE = '\U0001F7E5'
    FIRE = '\U0001F525'
    STAR = '\U00002B50'


class BalanceManager:

    def __init__(self):
        self.last_known_balance = BalanceDB.get_balance()

    @staticmethod
    def update_last_known_balance(new_balance: float):
        BalanceDB.store_balance(value=new_balance)

    def calculate_perc_change(self, new_balance: float) -> float:
        if self.last_known_balance != 0:
            perc_change = ((new_balance - self.last_known_balance) / self.last_known_balance) * 100
            return perc_change
        return 0

    def calculate_change(self, new_balance: float) -> float:
        return new_balance - self.last_known_balance


def main():
    binance_client = BinanceClient()
    balance_manager = BalanceManager()

    current_balance = binance_client.get_total_stable_coins_balance()

    change = balance_manager.calculate_change(current_balance)
    balance_manager.update_last_known_balance(current_balance)

    msg = MessageBuilder.build_message(current_balance, change)

    messenger = TelegramMessenger()
    messenger.send_message(msg)


if __name__ == '__main__':
    main()

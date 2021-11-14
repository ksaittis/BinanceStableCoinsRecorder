import os

from binance import Client

from storage_manager import StorageManager


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


class BalanceManager:

    def __init__(self):
        self.client = BinanceClient()
        self.storage_manager = StorageManager()
        self.last_balance_record = self.storage_manager.get_latest_balance()

    def get_available_stablecoins_balance(self):
        return self.client.get_total_stable_coins_balance()

    def update_last_known_balance(self, balance_value: float):
        self.storage_manager.store_balance(balance_value)

    def calculate_change(self, new_balance: float) -> float:
        return new_balance - self.get_latest_balance_value()

    def get_latest_balance_value(self) -> float:
        return self.last_balance_record.value

    def get_latest_balance_timestamp(self):
        return self.last_balance_record.timestamp

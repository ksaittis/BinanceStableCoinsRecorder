import logging
import os
from datetime import datetime
from pathlib import Path

from tinydb import TinyDB


class TimeHelper:
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def get_current_timestamp() -> str:
        return datetime.utcnow().strftime(TimeHelper.DATETIME_FORMAT)


class BalanceRecord:
    BALANCE = 'balance'
    TIMESTAMP = 'timestamp'

    def __init__(self, document: dict):
        self.value = document[BalanceRecord.BALANCE]
        self.timestamp = document[BalanceRecord.TIMESTAMP]

    @staticmethod
    def get_blank_record():
        return BalanceRecord(document={
            BalanceRecord.BALANCE: 0,
            BalanceRecord.TIMESTAMP: TimeHelper.get_current_timestamp()
        })

    def get_value(self) -> float:
        return self.value

    def get_timestamp(self) -> str:
        return self.timestamp


class StorageManager:
    BALANCE = 'balance'
    TIMESTAMP = 'timestamp'

    def __init__(self, path=None):
        if path is None:
            # Create data dir
            data_dir: str = os.getenv('DB_DATA_DIR', "/data/db")
            Path(data_dir).mkdir(parents=True, exist_ok=True)
            self._db_file = open(f'{data_dir}/balance_db.json', 'a+')
            path = self._db_file.name
            logging.info(f'Created db file at path {path}')

        self._db = TinyDB(path)

    def store_balance(self, balance: float) -> None:
        self._db.insert(
            {
                self.BALANCE: balance,
                self.TIMESTAMP: TimeHelper.get_current_timestamp(),
            }
        )

    def get_latest_balance(self) -> BalanceRecord:
        if len(self._db.all()) > 0:
            # Getting last document id
            last_doc_id = self._db.all()[-1].doc_id
            last_document = self._db.get(doc_id=last_doc_id)
            return BalanceRecord(last_document)
        # if no records exist, return a blank one
        return BalanceRecord.get_blank_record()

import os
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build

from storage_manager import TimeHelper

STABLECOINS_BALANCE_SPREADSHEET_ID = os.getenv('STABLECOINS_BALANCE_SPREADSHEET_ID',
                                               '1WlGVDulawNkB8sp1ZXtylPRMLSm1UyVAYJlDGIIH2AE')
STABLECOINS_SPREADSHEET = os.getenv('STABLECOINS_SPREADSHEET', 'Stablecoins')


class GoogleSheetsClient:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE_PATH', './service.json')
    API = 'sheets'
    API_VERSION = 'v4'

    def __init__(self, sheet_id: str, spreadsheet_name: str):
        self.sheet_id = sheet_id
        self.spreadsheet_name = spreadsheet_name
        self._speadsheet_service = self._build_service().spreadsheets()

    def set_spreadsheet_name(self, spreadsheet_name: str):
        self.spreadsheet_name = spreadsheet_name

    def _get_creds(self):
        return service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)

    def _build_service(self):
        return build('sheets', 'v4', credentials=self._get_creds())

    def get_values_in_range(self, cell_range: str):
        result = self._speadsheet_service.values().get(spreadsheetId=self.sheet_id,
                                                       range=f'{self.spreadsheet_name}!{cell_range}'
                                                       ).execute()
        return result.get('values', [])

    def update_sheet(self, starting_cell: str, data: dict):
        self._speadsheet_service.values().update(spreadsheetId=self.sheet_id,
                                                 range=f'{self.spreadsheet_name}!{starting_cell}',
                                                 valueInputOption='USER_ENTERED',
                                                 body=data
                                                 ).execute()

    def append_sheet(self, data: List[List[str]]):
        self._speadsheet_service.values().append(spreadsheetId=self.sheet_id,
                                                 range=f'{self.spreadsheet_name}!A2',
                                                 valueInputOption='USER_ENTERED',
                                                 insertDataOption='INSERT_ROWS',
                                                 body={
                                                     "majorDimension": "ROWS",
                                                     'values': data
                                                 }
                                                 ).execute()


class GoogleSheetsManager:

    def __init__(self):
        self._client = GoogleSheetsClient(sheet_id=STABLECOINS_BALANCE_SPREADSHEET_ID,
                                          spreadsheet_name=STABLECOINS_SPREADSHEET)

    def append_data(self, data: List[List[str]]):
        self._client.append_sheet(data)

    def get_data(self, cell_range='A1:B100'):
        return self._client.get_values_in_range(cell_range=cell_range)

    def store_new_balance(self, balance: float):
        self.append_data([[TimeHelper.get_current_timestamp(), str(balance)]])


def main():
    g = GoogleSheetsManager()

    data = [[TimeHelper.get_current_timestamp(), '15000.356']]
    g.append_data(data=data)

    print(g.get_data())


if __name__ == '__main__':
    main()

import logging

from dotenv import load_dotenv

from balance_manager import BalanceManager
from message_manager import MessageManager

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def main():
    balance_manager = BalanceManager()
    message_manager = MessageManager()

    current_balance = balance_manager.get_available_stablecoins_balance()

    change = balance_manager.calculate_change(current_balance)
    balance_manager.update_last_known_balance(current_balance)

    msg = message_manager.build_message(current_balance, change)
    logging.info(msg.text())
    # message_manager.send_message(msg)


if __name__ == '__main__':
    main()

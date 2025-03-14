from config import USDT_TON_WALLET

def get_payment_message():
    return f"💰 Для подписки отправьте 5 USDT (TON) на кошелек:\n\n`{USDT_TON_WALLET}`\n\nПосле оплаты отправьте /confirm."

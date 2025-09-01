import os
import time
import random
from datetime import datetime
import requests


def write_signal_csv(model_output_path: str, signal: int, quantity: int, coin_symbol: str) -> None:
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    signal_str = 'BUY' if signal == 1 else 'HOLD'
    with open(model_output_path, 'a') as f:
        f.write(f"{now_str}, {signal_str}, {quantity}, {coin_symbol}\n")


def post_webhook(url: str, signal: int, price: float, reasoning: str = "Test model signal") -> None:
    payload = {
        "type": "model_signal",
        "data": {
            "timestamp": datetime.now().isoformat(),
            "signal": 'BUY' if signal == 1 else 'HOLD',
            "confidence": round(random.uniform(0.6, 0.95), 4),
            "price": price,
            "reasoning": reasoning,
        },
        "timestamp": datetime.now().isoformat(),
    }
    try:
        requests.post(url, json=payload, timeout=3)
    except Exception:
        pass


def main():
    print('Starting TEST model (random BUY/HOLD)...')

    # Output CSV path
    model_output_path = os.path.abspath(os.path.join('..', '..', '..', 'logs', 'model_output.csv'))
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    target_coin = 'CHZ/USDT'
    webhook_url = 'http://localhost:5001/webhook'

    # Ensure file exists
    if not os.path.exists(model_output_path):
        open(model_output_path, 'a').close()

    while True:
        signal = random.choice([0, 1])
        price = round(random.uniform(150, 250), 2)

        write_signal_csv(model_output_path, signal, 1, target_coin)
        post_webhook(webhook_url, signal, price)

        print(f"Emitted test signal: {'BUY' if signal == 1 else 'HOLD'} @ {price}")
        time.sleep(10)


if __name__ == '__main__':
    main()

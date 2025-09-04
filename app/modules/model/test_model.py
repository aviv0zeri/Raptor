import os
import sys
import time
import random
from datetime import datetime
import builtins as _builtins

def _ts_print(*args, **kwargs):
    try:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if args:
            first = f"[{ts}] {args[0]}"
            _builtins.print(first, *args[1:], **kwargs)
        else:
            _builtins.print(f"[{ts}]", **kwargs)
    except Exception:
        _builtins.print(*args, **kwargs)

print = _ts_print  # type: ignore
import requests
from dataclasses import asdict, dataclass

# Ensure project root is on sys.path for package imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from app.modules.components.signal import Signal
except Exception:
    @dataclass
    class Signal:
        timestamp: str
        signal: str
        confidence: float
        reasoning: str
from pathlib import Path


def write_signal_csv(model_output_path: str, signal: int, quantity: int, coin_symbol: str) -> None:
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    signal_str = 'BUY' if signal == 1 else 'HOLD'
    with open(model_output_path, 'a') as f:
        f.write(f"{now_str}, {signal_str}, {quantity}, {coin_symbol}\n")


 

def post_signal_via_api(api_url: str, sig: Signal) -> None:
    """Send signal JSON to API which forwards to webhook."""
    try:
        requests.post(api_url, json={"data": asdict(sig)}, timeout=2)
    except Exception:
        pass


def main():
    print('Starting TEST model (random BUY/HOLD)...')

    # Resolve project root and logs dir deterministically
    project_root = Path(__file__).resolve().parents[3]
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Output CSV path (test-specific)
    model_output_path = str(logs_dir / 'model_output_test.csv')
    target_coin = 'CHZ/USDT'
    api_url = os.environ.get('API_SIGNAL_URL', 'http://localhost:5050/api/model/signal')
    webhook_url = os.environ.get('WEBHOOK_URL', 'http://localhost:5001/webhook')

    # Ensure file exists
    if not os.path.exists(model_output_path):
        open(model_output_path, 'a').close()

    model_name = os.environ.get('MODEL_NAME', 'test')
    interval = os.environ.get('MODEL_INTERVAL', '1m')

    # Map interval strings to seconds
    def interval_to_seconds(val: str) -> int:
        val = (val or '').lower()
        if val.endswith('s'):
            try:
                return int(val[:-1])
            except Exception:
                return 2
        if val.endswith('m'):
            try:
                return int(val[:-1]) * 60
            except Exception:
                return 60
        if val.endswith('h'):
            try:
                return int(val[:-1]) * 3600
            except Exception:
                return 3600
        return 2

    sleep_seconds = max(1, interval_to_seconds(interval))

    while True:
        signal = random.choice([0, 1])
        price = round(random.uniform(150, 250), 2)

        write_signal_csv(model_output_path, signal, 1, target_coin)
        sig = Signal(
            timestamp=datetime.now().isoformat(),
            signal='BUY' if signal == 1 else 'HOLD',
            confidence=round(random.uniform(0.6, 0.95), 4),
            reasoning='Test model signal'
        )
        # Tag model and interval and send via API
        payload = {"data": {**asdict(sig), "model": model_name, "interval": interval}}
        try:
            r = requests.post(api_url, json=payload, timeout=(1, 3))
            # print minimal trace for debugging
            print(f"Test model posted: {r.status_code}")
        except Exception as e:
            print(f"Test model post failed (API): {e}")
            # Fallback: post directly to webhook
            try:
                direct = {"type": "model_signal", "data": payload["data"], "timestamp": datetime.now().isoformat()}
                r2 = requests.post(webhook_url, json=direct, timeout=(1, 3))
                print(f"Test model posted to webhook: {r2.status_code}")
            except Exception as e2:
                print(f"Test model webhook post failed: {e2}")

        print(f"Emitted test signal: {'BUY' if signal == 1 else 'HOLD'} @ {price}")
        time.sleep(sleep_seconds)


if __name__ == '__main__':
    main()

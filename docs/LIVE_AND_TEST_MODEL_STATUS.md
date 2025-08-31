# Model Status Summary

## Live Model
- Schedule: every 10 seconds
- Data: Pulling real Binance candles (files in `app/Data/rawdata/`)
- Output: Signals appended to `/Users/aviv0zeri/work/personal/model_output.csv`
- Known warnings: urllib3 OpenSSL/LibreSSL warning (safe to ignore locally)

## Test Model
- Emits random BUY/HOLD every 10 seconds
- Output: Same CSV format as live model
- Webhook: Posts `type=model_signal` payloads to `http://localhost:5001/webhook`

## Webhook Server
- HTTP: `http://localhost:5001/webhook`
- WebSocket: `ws://localhost:8765`
- Recent events: `GET http://localhost:5001/api/events`

## Next Steps
- Continue UI integration with Model Reader
- Display live signals and logs in dashboard
- Expand to object-oriented signal classes for UI responsiveness

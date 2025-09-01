import React, { useEffect, useRef, useState } from 'react';

export default function SignalWall() {
  const [signals, setSignals] = useState([]);
  const [clock, setClock] = useState(new Date());
  const [busy, setBusy] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WS connected');
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg?.type === 'model_signal' && msg?.data) {
          const s = {
            timestamp: msg.data.timestamp || new Date().toISOString(),
            signal: msg.data.signal || 'HOLD',
            confidence: msg.data.confidence ?? 0.5,
            price: msg.data.price ?? 0,
            reasoning: msg.data.reasoning || '',
          };
          setSignals((prev) => [s, ...prev].slice(0, 50));
          if (window?.soundsInterface) window.soundsInterface.playTradeSignal();
        }
      } catch (e) {
        console.warn('WS parse error', e);
      }
    };

    ws.onerror = (e) => console.warn('WS error', e);
    ws.onclose = () => console.log('WS closed');

    return () => ws.close();
  }, []);

  useEffect(() => {
    const t = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const callApi = async (path) => {
    try {
      setBusy(true);
      const res = await fetch(`http://localhost:5050${path}`, { method: 'POST' });
      await res.json().catch(() => ({}));
    } catch (e) {
      console.warn('API call failed', e);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{
      backgroundColor: '#000',
      color: '#fff',
      width: '100vw',
      height: '100vh',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      padding: '24px',
      boxSizing: 'border-box',
      fontFamily: 'system-ui, Arial, sans-serif'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: 24, fontWeight: 700 }}>Raptor Signal Wall</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button
            onClick={() => callApi('/api/test-stack/start')}
            disabled={busy}
            style={{ background: '#fff', color: '#000', border: 'none', padding: '8px 12px', borderRadius: 6, cursor: 'pointer' }}
          >Start</button>
          <button
            onClick={() => callApi('/api/test-stack/stop')}
            disabled={busy}
            style={{ background: '#444', color: '#fff', border: '1px solid #666', padding: '8px 12px', borderRadius: 6, cursor: 'pointer' }}
          >Stop</button>
          <div style={{ fontSize: 18, opacity: 0.85 }}>{clock.toLocaleTimeString()}</div>
        </div>
      </div>

      <div style={{ flex: 1, display: 'flex', gap: 24, marginTop: 24 }}>
        <div style={{ flex: 2, display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontSize: 18, marginBottom: 12, opacity: 0.8 }}>Recent Signals</div>
          <div style={{
            flex: 1,
            border: '1px solid #333',
            borderRadius: 8,
            padding: 16,
            display: 'grid',
            gridTemplateColumns: '180px 100px 120px 1fr',
            columnGap: 12,
            rowGap: 10,
            alignContent: 'start'
          }}>
            <div style={{ opacity: 0.6 }}>Time</div>
            <div style={{ opacity: 0.6 }}>Signal</div>
            <div style={{ opacity: 0.6 }}>Price</div>
            <div style={{ opacity: 0.6 }}>Reason</div>
            {signals.map((s, idx) => (
              <React.Fragment key={idx}>
                <div>{new Date(s.timestamp).toLocaleTimeString()}</div>
                <div style={{ color: s.signal === 'BUY' ? '#4caf50' : '#bbb', fontWeight: 700 }}>{s.signal}</div>
                <div>${Number(s.price).toFixed(2)}</div>
                <div style={{ opacity: 0.8 }}>{s.reasoning}</div>
              </React.Fragment>
            ))}
          </div>
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontSize: 18, marginBottom: 12, opacity: 0.8 }}>Logs</div>
          <div style={{
            flex: 1,
            border: '1px solid #333',
            borderRadius: 8,
            padding: 16,
            overflow: 'hidden',
            whiteSpace: 'pre-wrap',
            opacity: 0.7
          }}>
            <div>Showing model build to signal logs here (placeholder)</div>
          </div>
        </div>
      </div>
    </div>
  );
}

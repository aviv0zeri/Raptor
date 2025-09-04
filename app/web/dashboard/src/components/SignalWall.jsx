import React, { useEffect, useRef, useState } from 'react';

export default function SignalWall() {
  const [signals, setSignals] = useState([]);
  const [clock, setClock] = useState(new Date());
  const [busy, setBusy] = useState(false);
  const [started, setStarted] = useState(false);
  const [model, setModel] = useState('real');
  const [intervalSel, setIntervalSel] = useState('1m');
  const [wsAttempts, setWsAttempts] = useState(0);
  const [realModelReady, setRealModelReady] = useState(false);
  const [realModelStatus, setRealModelStatus] = useState('Not started');
  const [initLogs, setInitLogs] = useState([]);
  const wsRef = useRef(null);

  // WebSocket with simple retry
  useEffect(() => {
    let closed = false;
    function connect() {
      const h = window.location.hostname;
      const wsUrl = `ws://${h}:8767`;
      console.log('Connecting WS to', wsUrl);
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WS connected');
        setWsAttempts(0);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg?.type === 'model_signal' && msg?.data) {
            const s = new Signal(msg.data);
            setSignals((prev) => [s, ...prev].slice(0, 50));
            if (window?.soundsInterface) window.soundsInterface.playTradeSignal();
          } else if (msg?.type === 'model_status' && msg?.data?.model === 'real') {
            // Handle Real model status updates
            const statusData = msg.data;
            setRealModelStatus(statusData.message || 'Initializing...');
            setRealModelReady(statusData.ready === true);
            
            // Add to initialization logs
            const logEntry = {
              timestamp: new Date().toLocaleTimeString(),
              message: statusData.message,
              type: statusData.status_type || 'info'
            };
            setInitLogs(prev => [logEntry, ...prev].slice(0, 20)); // Keep last 20 logs
          }
        } catch (e) {
          console.warn('WS parse error', e);
        }
      };

      ws.onerror = (e) => console.warn('WS error', e);
      ws.onclose = () => {
        console.log('WS closed');
        if (!closed) {
          const next = Math.min(5000, 500 * (wsAttempts + 1));
          setWsAttempts((n) => n + 1);
          setTimeout(connect, next);
        }
      };
    }
    // Add delay to ensure WebSocket server is ready
    setTimeout(connect, 2000);
    return () => {
      closed = true;
      try { wsRef.current?.close(); } catch (_) {}
    };
  }, []);

  // Clear signals when model changes
  useEffect(() => { setSignals([]); }, [model]);

  // Fallback polling in case WS fails
  useEffect(() => {
    const t = setInterval(async () => {
      try {
        const host = (window.location.hostname === 'localhost' || window.location.hostname === '::1')
          ? '127.0.0.1'
          : window.location.hostname;
        const r = await fetch(`http://${host}:5001/api/events`);
        const j = await r.json();
        (j.events || []).forEach((msg) => {
          if (msg?.type === 'model_signal' && msg?.data) {
            const s = new Signal(msg.data);
            setSignals((prev) => [s, ...prev].slice(0, 50));
          }
        });
      } catch (_) {}
    }, 1000);
    return () => clearInterval(t);
  }, []);

  // Signal class for consistency
  class Signal {
    constructor(data) {
      this.timestamp = data.timestamp || new Date().toISOString();
      this.signal = data.signal || 'HOLD';
      this.confidence = data.confidence ?? 0.5;
      this.reasoning = data.reasoning || '';
    }
  }

  useEffect(() => {
    const t = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  // Check model status periodically
  useEffect(() => {
    checkModelStatus();
    const statusInterval = setInterval(checkModelStatus, 3000); // Check every 3 seconds
    return () => clearInterval(statusInterval);
  }, [model]);

  const checkModelStatus = async () => {
    try {
      const apiUrl = `http://${window.location.hostname}:5050/api/model/status`;
      const res = await fetch(apiUrl);
      const body = await res.json().catch(() => ({}));
      setRealModelReady(body.real_model_ready || false);
      setStarted(body.real_model_running || body.running || false);
      
      // Update status based on new flow
      if (model === 'real') {
        if (!body.running) {
          setRealModelStatus('Not started');
        } else if (body.running && !body.real_model_ready) {
          setRealModelStatus('Building...');
        } else if (body.real_model_ready && !body.real_model_running) {
          setRealModelStatus('Ready');
        } else if (body.real_model_running) {
          setRealModelStatus('Running');
        }
      }
    } catch (e) {
      console.warn('Status check failed', e);
    }
  };

  const callApi = async (path) => {
    try {
      setBusy(true);
      console.log('Calling API:', path);
      const apiUrl = `http://${window.location.hostname}:5050${path}`;
      const payload = path.includes('/model/start') ? { model, interval: intervalSel } : undefined;
      const res = await fetch(apiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: payload ? JSON.stringify(payload) : undefined });
      const body = await res.json().catch(() => ({}));
      console.log('API response:', body);
      if (path.includes('/model/start')) setStarted(!!body?.success);
      if (path.includes('/model/stop')) setStarted(false);
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
      display: 'grid',
      gridTemplateRows: '64px 1fr',
      padding: 0,
      boxSizing: 'border-box',
      fontFamily: 'system-ui, Arial, sans-serif'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 24px' }}>
        <div style={{ fontSize: 24, fontWeight: 700 }}>Raptor Signal Wall</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <select value={model} onChange={(e) => setModel(e.target.value)} disabled={started} style={{ padding: '8px', borderRadius: 6 }}>
              <option value="real">Real model</option>
              <option value="test">Test</option>
            </select>
            {model === 'real' && (
              <div style={{ 
                fontSize: '12px', 
                color: realModelStatus === 'Ready' ? '#4caf50' : '#ff9800',
                fontWeight: 'bold',
                maxWidth: '200px'
              }}>
                {realModelStatus === 'Ready' ? '✓ Ready' : `⏳ ${realModelStatus}`}
              </div>
            )}
          </div>
          <select value={intervalSel} onChange={(e) => setIntervalSel(e.target.value)} disabled={started} style={{ padding: '8px', borderRadius: 6 }}>
            <option value="1m">1m</option>
            <option value="5m">5m</option>
            <option value="15m">15m</option>
            <option value="1h">1h</option>
            <option value="2h">2h</option>
            <option value="4h">4h</option>
          </select>
          <button
            onClick={() => started ? callApi('/api/model/stop') : callApi('/api/model/start')}
            disabled={busy}
            style={{
              background: started ? '#c62828' : '#2e7d32',
              color: '#ffffff',
              border: 'none',
              padding: '10px 16px',
              borderRadius: 8,
              cursor: 'pointer',
              transition: 'transform 80ms ease, background 120ms ease, box-shadow 120ms ease',
              boxShadow: started ? '0 0 0 2px rgba(198,40,40,0.35)' : '0 0 0 2px rgba(46,125,50,0.35)'
            }}
            onMouseDown={(e) => { e.currentTarget.style.transform = 'scale(0.97)'; }}
            onMouseUp={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}
          >{started ? 'Stop' : 'Start'}</button>
          <div style={{ fontSize: 18, opacity: 0.85 }}>{clock.toLocaleTimeString()}</div>
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24, padding: '0 24px 24px 24px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <div style={{ fontSize: 18, margin: '12px 0', opacity: 0.8 }}>Recent Signals</div>
          <div style={{
            flex: 1,
            minHeight: 0,
            border: '1px solid #333',
            borderRadius: 8,
            padding: 16,
            display: 'grid',
            gridTemplateColumns: '180px 120px 1fr',
            columnGap: 12,
            rowGap: 10,
            alignContent: 'start',
            overflow: 'hidden'
          }}>
            <div style={{ opacity: 0.6 }}>Time</div>
            <div style={{ opacity: 0.6 }}>Signal</div>
            <div style={{ opacity: 0.6 }}>Reason</div>
            {signals.map((s, idx) => (
              <React.Fragment key={idx}>
                <div>{new Date(s.timestamp).toLocaleTimeString()}</div>
                <div style={{ color: s.signal === 'BUY' ? '#4caf50' : s.signal === 'HOLD' ? '#ffca28' : '#bbb', fontWeight: 700 }}>{s.signal}</div>
                <div style={{ opacity: 0.8 }}>{s.reasoning}</div>
              </React.Fragment>
            ))}
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <div style={{ fontSize: 18, margin: '12px 0', opacity: 0.8 }}>Logs</div>
          <div style={{
            flex: 1,
            minHeight: 0,
            border: '1px solid #333',
            borderRadius: 8,
            padding: 16,
            overflow: 'hidden',
            whiteSpace: 'pre-wrap',
            opacity: 0.7
          }}>
{initLogs.length > 0 ? (
              initLogs.map((log, idx) => (
                <div key={idx} style={{ 
                  marginBottom: '4px', 
                  fontSize: '12px',
                  color: log.type === 'success' ? '#4caf50' : log.type === 'error' ? '#f44336' : '#fff'
                }}>
                  <span style={{ opacity: 0.7 }}>[{log.timestamp}]</span> {log.message}
                </div>
              ))
            ) : (
              <div style={{ opacity: 0.5 }}>Waiting for model initialization logs...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

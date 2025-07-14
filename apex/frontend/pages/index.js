import React, { useState, useEffect } from 'react';

export default function ApexDashboard() {
  const [buySignals, setBuySignals] = useState([]);
  const [performance, setPerformance] = useState({
    system: { tokens_scanned: 0, scan_rate: 0 },
    trading: { current_balance: 10, total_pnl: 0, win_rate: 0, total_trades: 0 }
  });
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      setConnected(true);
      console.log('🔌 Connected to APEX');
    };
    
    ws.onclose = () => {
      setConnected(false);
      setTimeout(() => window.location.reload(), 3000);
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'update') {
          setBuySignals(data.buy_signals || []);
          setPerformance(data.performance || performance);
        }
      } catch (e) {
        console.log('Parse error:', e);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#000000',
      color: '#10B981',
      fontFamily: 'Monaco, monospace',
      padding: '20px'
    }}>
      <div style={{ borderBottom: '2px solid #065F46', paddingBottom: '20px', marginBottom: '30px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '36px', fontWeight: 'bold', color: '#34D399', margin: 0 }}>
              ⚡ APEX TRADING SYSTEM
            </h1>
            <p style={{ color: '#065F46', margin: '8px 0 0 0', fontSize: '18px' }}>
              $10 → $1000 Ultra-Aggressive Engine
            </p>
          </div>
          
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '10px',
            color: connected ? '#10B981' : '#EF4444',
            fontSize: '16px',
            fontWeight: 'bold'
          }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: connected ? '#10B981' : '#EF4444'
            }}></div>
            {connected ? '🟢 LIVE' : '🔴 OFFLINE'}
          </div>
        </div>
        
        <div style={{ 
          marginTop: '25px',
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '20px'
        }}>
          <div style={{ textAlign: 'center', padding: '15px', backgroundColor: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px' }}>
            <div style={{ color: '#34D399', fontWeight: 'bold', fontSize: '24px' }}>
              ${performance.trading.current_balance.toFixed(2)}
            </div>
            <div style={{ color: '#065F46' }}>Balance</div>
          </div>
          <div style={{ textAlign: 'center', padding: '15px', backgroundColor: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px' }}>
            <div style={{ color: '#34D399', fontWeight: 'bold', fontSize: '24px' }}>
              {(performance.trading.win_rate * 100).toFixed(1)}%
            </div>
            <div style={{ color: '#065F46' }}>Win Rate</div>
          </div>
          <div style={{ textAlign: 'center', padding: '15px', backgroundColor: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px' }}>
            <div style={{ color: '#34D399', fontWeight: 'bold', fontSize: '24px' }}>
              {performance.system.scan_rate || 0}/s
            </div>
            <div style={{ color: '#065F46' }}>Scan Rate</div>
          </div>
          <div style={{ textAlign: 'center', padding: '15px', backgroundColor: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px' }}>
            <div style={{ color: '#34D399', fontWeight: 'bold', fontSize: '24px' }}>
              {buySignals.length}
            </div>
            <div style={{ color: '#065F46' }}>Signals</div>
          </div>
        </div>
      </div>

      <div>
        <h2 style={{ 
          fontSize: '28px', 
          fontWeight: 'bold', 
          color: '#34D399', 
          marginBottom: '20px',
          textAlign: 'center'
        }}>
          🚀 LIVE BUY SIGNALS
        </h2>
        
        <div style={{ 
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '20px',
          maxHeight: '70vh',
          overflowY: 'auto'
        }}>
          {buySignals.map((signal, index) => (
            <div
              key={signal.address}
              style={{
                border: '2px solid #065F46',
                borderRadius: '12px',
                padding: '20px',
                backgroundColor: 'rgba(17, 24, 39, 0.9)',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.4)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
                <div>
                  <div style={{ fontWeight: 'bold', color: '#34D399', fontSize: '24px' }}>
                    {signal.symbol}
                  </div>
                  <div style={{ fontSize: '12px', color: '#065F46' }}>
                    {signal.address.slice(0, 8)}...{signal.address.slice(-6)}
                  </div>
                </div>
                
                <div style={{ textAlign: 'right' }}>
                  <div style={{
                    padding: '8px 12px',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: 'bold',
                    backgroundColor: signal.urgency >= 8 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                    color: signal.urgency >= 8 ? '#EF4444' : '#10B981',
                    border: `1px solid ${signal.urgency >= 8 ? '#EF4444' : '#10B981'}`
                  }}>
                    URGENCY {signal.urgency}
                  </div>
                </div>
              </div>
              
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: '1fr 1fr', 
                gap: '15px',
                marginBottom: '15px'
              }}>
                <div>
                  <div style={{ color: '#065F46', marginBottom: '5px' }}>Price</div>
                  <div style={{ color: '#10B981', fontWeight: 'bold', fontSize: '16px' }}>
                    ${signal.current_price.toFixed(6)}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#065F46', marginBottom: '5px' }}>Expected Return</div>
                  <div style={{ color: '#34D399', fontWeight: 'bold', fontSize: '18px' }}>
                    +{(signal.expected_return * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
              
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                fontSize: '14px',
                borderTop: '1px solid #065F46',
                paddingTop: '12px'
              }}>
                <span>
                  Confidence: <strong style={{ color: '#10B981' }}>
                    {(signal.confidence * 100).toFixed(0)}%
                  </strong>
                </span>
                <span>
                  Type: <strong style={{ color: '#F59E0B' }}>
                    {signal.type}
                  </strong>
                </span>
              </div>
            </div>
          ))}
          
          {buySignals.length === 0 && (
            <div style={{ 
              gridColumn: '1 / -1',
              textAlign: 'center', 
              color: '#065F46', 
              padding: '60px 20px',
              fontSize: '18px'
            }}>
              <div style={{ fontSize: '72px', marginBottom: '20px' }}>🔍</div>
              <div>
                {connected ? 'Scanning for 95%+ confidence opportunities...' : 'Connecting to APEX...'}
              </div>
              <div style={{ fontSize: '14px', marginTop: '10px', color: '#047857' }}>
                Ultra-fast momentum detection active
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
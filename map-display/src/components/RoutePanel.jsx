// src/components/RoutePanel.jsx
import { Warehouse, Package } from 'lucide-react';

function RoutePanel({ locations }) {
  return (
    <div
      style={{
        position: 'absolute',
        top: '16px',
        right: '16px',
        zIndex: 1000,
        background: 'rgba(255,255,255,0.97)',
        backdropFilter: 'blur(6px)',
        borderRadius: '12px',
        boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
        padding: '18px',
        width: '230px',
        maxHeight: '80vh',
        overflowY: 'auto',
      }}
    >
      <h3 style={{ margin: '0 0 14px 0', fontSize: '14px', fontWeight: 700, color: '#065f46', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
        Route Order
      </h3>
      <div>
        {locations.map((loc, index) => {
          const isDepot = loc.type === 'depot';
          const isLast = index === locations.length - 1;
          return (
            <div key={`${loc.id}-${index}`} style={{ display: 'flex', gap: '10px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div
                  style={{
                    width: '26px',
                    height: '26px',
                    borderRadius: '50%',
                    background: isDepot ? '#1e293b' : '#059669',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  {isDepot ? <Warehouse size={13} color="white" /> : <Package size={13} color="white" />}
                </div>
                {!isLast && <div style={{ width: '2px', flex: 1, background: '#d1d5db', minHeight: '18px' }} />}
              </div>
              <div style={{ paddingBottom: '18px', fontSize: '13px' }}>
                <div style={{ fontWeight: 600, color: '#1e293b' }}>{loc.name}</div>
                {!isDepot && (
                  <div style={{ color: '#64748b', fontSize: '11px' }}>Stop {index}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default RoutePanel;
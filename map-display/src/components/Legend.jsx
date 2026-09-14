// src/components/Legend.jsx
import { Warehouse, Package } from 'lucide-react';

function Legend() {
  return (
    <div
      style={{
        position: 'absolute',
        bottom: '20px',
        left: '16px',
        zIndex: 1000,
        background: 'rgba(255,255,255,0.95)',
        backdropFilter: 'blur(6px)',
        borderRadius: '10px',
        boxShadow: '0 4px 14px rgba(0,0,0,0.15)',
        padding: '12px 16px',
        fontSize: '12.5px',
        fontWeight: 500,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
        <div style={{ background: '#1e293b', borderRadius: '50%', width: '22px', height: '22px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Warehouse size={12} color="white" />
        </div>
        <span style={{ color: '#334155' }}>Depot</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{ background: '#059669', borderRadius: '50%', width: '22px', height: '22px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Package size={12} color="white" />
        </div>
        <span style={{ color: '#334155' }}>Delivery Stop</span>
      </div>
    </div>
  );
}

export default Legend;
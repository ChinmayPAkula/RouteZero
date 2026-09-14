// src/components/Header.jsx
import { Leaf } from 'lucide-react';

function Header() {
  return (
    <div
      style={{
        position: 'absolute',
        top: '16px',
        left: '16px',
        zIndex: 1000,
        background: 'linear-gradient(135deg, #065f46, #047857)',
        borderRadius: '12px',
        boxShadow: '0 4px 16px rgba(0,0,0,0.25)',
        padding: '14px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        color: 'white',
      }}
    >
      <div
        style={{
          background: 'rgba(255,255,255,0.15)',
          borderRadius: '8px',
          padding: '6px',
          display: 'flex',
        }}
      >
        <Leaf size={20} color="#a7f3d0" />
      </div>
      <div>
        <h2 style={{ margin: 0, fontSize: '17px', fontWeight: 700, letterSpacing: '0.3px' }}>
          RouteZero
        </h2>
        <p style={{ margin: 0, fontSize: '11px', color: '#a7f3d0', fontWeight: 400 }}>
          Carbon-Aware Logistics
        </p>
      </div>
    </div>
  );
}

export default Header;
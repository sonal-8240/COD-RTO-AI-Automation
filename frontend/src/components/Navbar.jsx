import React from 'react';
import { 
  LayoutDashboard, 
  SearchCode, 
  MessageSquare, 
  Table, 
  LineChart, 
  Sliders, 
  ShieldCheck, 
  Activity,
  Zap
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, systemStatus }) {
  const navItems = [
    { id: 'dashboard', label: 'Founder Dashboard', icon: LayoutDashboard },
    { id: 'evaluator', label: 'Live Risk Evaluator', icon: SearchCode },
    { id: 'whatsapp', label: 'WhatsApp Simulator', icon: MessageSquare },
    { id: 'orders', label: 'Orders & Registry', icon: Table },
    { id: 'findings', label: 'Empirical Findings', icon: LineChart },
    { id: 'settings', label: 'Settings & Economics', icon: Sliders },
  ];

  return (
    <header className="navbar">
      <div className="nav-brand">
        <div className="nav-logo-icon">
          <span>SC</span>
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="nav-brand-title">SmartCOD AI</span>
            <span style={{ 
              fontSize: '10px', 
              fontWeight: 800, 
              backgroundColor: 'rgba(59, 130, 246, 0.18)', 
              color: '#60a5fa', 
              padding: '2px 6px', 
              borderRadius: '4px',
              letterSpacing: '0.04em'
            }}>
              v1.0 PRO
            </span>
          </div>
          <div className="nav-brand-subtitle">Intelligent COD Risk & RTO Prevention</div>
        </div>
      </div>

      <nav className="nav-tabs">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-tab-btn ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={15} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px', 
          backgroundColor: 'rgba(255, 255, 255, 0.04)', 
          border: '1px solid rgba(255, 255, 255, 0.08)',
          padding: '6px 12px',
          borderRadius: '9999px',
          fontSize: '12px'
        }}>
          <span 
            className="status-beacon" 
            style={{ backgroundColor: systemStatus === 'online' ? '#10b981' : '#f43f5e' }} 
          />
          <span style={{ 
            color: systemStatus === 'online' ? '#34d399' : '#f87171', 
            fontWeight: 700, 
            letterSpacing: '0.02em',
            fontSize: '11px',
            textTransform: 'uppercase'
          }}>
            {systemStatus === 'online' ? 'Engine Online' : 'Connecting'}
          </span>
        </div>
      </div>
    </header>
  );
}

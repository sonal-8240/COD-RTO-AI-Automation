import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import FounderDashboard from './pages/FounderDashboard';
import OrderEvaluator from './pages/OrderEvaluator';
import WhatsAppSimulator from './pages/WhatsAppSimulator';
import OrdersTable from './pages/OrdersTable';
import RiskFindings from './pages/RiskFindings';
import SettingsPanel from './pages/SettingsPanel';
import { getHealth } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemStatus, setSystemStatus] = useState('connecting');
  const [selectedOrderIdForWhatsApp, setSelectedOrderIdForWhatsApp] = useState('KT100001');
  const [selectedWorkflowForWhatsApp, setSelectedWorkflowForWhatsApp] = useState('CONFIRMATION');

  useEffect(() => {
    checkBackendHealth();
    const interval = setInterval(checkBackendHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkBackendHealth = async () => {
    try {
      const res = await getHealth();
      if (res.data?.status === 'healthy') {
        setSystemStatus('online');
      }
    } catch (err) {
      setSystemStatus('offline');
    }
  };

  const handleOpenWhatsApp = (orderId, workflow = 'CONFIRMATION') => {
    setSelectedOrderIdForWhatsApp(orderId);
    setSelectedWorkflowForWhatsApp(workflow);
    setActiveTab('whatsapp');
  };

  return (
    <div className="app-container">
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        systemStatus={systemStatus} 
      />

      <main className="main-content">
        {activeTab === 'dashboard' && <FounderDashboard />}
        {activeTab === 'evaluator' && (
          <OrderEvaluator onSwitchToWhatsApp={handleOpenWhatsApp} />
        )}
        {activeTab === 'whatsapp' && (
          <WhatsAppSimulator 
            initialOrderId={selectedOrderIdForWhatsApp} 
            initialWorkflow={selectedWorkflowForWhatsApp} 
          />
        )}
        {activeTab === 'orders' && (
          <OrdersTable onOpenWhatsApp={handleOpenWhatsApp} />
        )}
        {activeTab === 'findings' && <RiskFindings />}
        {activeTab === 'settings' && <SettingsPanel />}
      </main>

      <footer style={{ 
        borderTop: '1px solid var(--border-color)', 
        padding: '20px 32px', 
        fontSize: '12px', 
        color: 'var(--text-muted)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px',
        backgroundColor: 'var(--bg-secondary)'
      }}>
        <div>
          <strong>SmartCOD AI</strong> • Intelligent COD Risk & RTO Prevention System v1.0.0
        </div>
        <div>
          Built with React 18, Vite, FastAPI, SQLite, and Scikit-learn
        </div>
      </footer>
    </div>
  );
}

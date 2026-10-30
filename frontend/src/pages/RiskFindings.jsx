import React, { useState, useEffect } from 'react';
import { 
  LineChart, 
  Database, 
  AlertTriangle, 
  TrendingUp, 
  FileText, 
  ShieldCheck,
  CheckCircle2,
  Users,
  MapPin,
  Truck
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  CartesianGrid,
  Legend
} from 'recharts';
import { getAnalysisFindings } from '../services/api';

export default function RiskFindings() {
  const [findings, setFindings] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFindings();
  }, []);

  const fetchFindings = async () => {
    try {
      const res = await getAnalysisFindings();
      setFindings(res.data);
    } catch (err) {
      console.error("Findings error:", err);
    } finally {
      setLoading(false);
    }
  };

  const finding1Data = [
    { segment: 'Clean Repeat (0 RTO)', rto_rate: 14.00, volume: 350, fill: '#10b981' },
    { segment: 'First-Time Shopper', rto_rate: 30.23, volume: 1495, fill: '#3b82f6' },
    { segment: 'Repeat with Prior RTO', rto_rate: 45.07, volume: 142, fill: '#f43f5e' }
  ];

  const finding2Data = [
    { tier: 'Tier 1: Structured (>35 chars)', rto_rate: 23.94, volume: 1412, fill: '#10b981' },
    { tier: 'Tier 2: Ambiguous (20-35 chars)', rto_rate: 27.60, volume: 393, fill: '#f59e0b' },
    { tier: 'Tier 3: Defective (<20 chars / "xyz")', rto_rate: 61.75, volume: 183, fill: '#f43f5e' }
  ];

  const courierData = [
    { courier: 'Delhivery', rto_rate: 26.04, fill: '#10b981' },
    { courier: 'Shadowfax', rto_rate: 28.47, fill: '#3b82f6' },
    { courier: 'Bluedart', rto_rate: 28.91, fill: '#8b5cf6' },
    { courier: 'Xpressbees', rto_rate: 30.95, fill: '#f43f5e' }
  ];

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 800 }}>Empirical Data Analysis & Key Findings</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
          Ground truth statistical discoveries from 1,988 deduplicated historical COD orders that drive the SmartCOD AI decision engine.
        </p>
      </div>

      {/* Dataset Summary Stat Ribbon */}
      <div className="card" style={{ marginBottom: '24px', padding: '16px 24px', backgroundColor: 'var(--bg-secondary)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Historical Orders
            </div>
            <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>
              1,988 Deduplicated
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              (30 duplicate pairs resolved)
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Global COD RTO Rate
            </div>
            <div style={{ fontSize: '20px', fontWeight: 800, color: '#f87171', fontFamily: 'var(--font-mono)' }}>
              28.43%
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              565 RTOs vs 1,422 Delivered
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Unique Pincodes
            </div>
            <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>
              461 Pincodes
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              Empirical Bayes smoothed
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Baseline RTO Cash Loss
            </div>
            <div style={{ fontSize: '20px', fontWeight: 800, color: '#f43f5e', fontFamily: 'var(--font-mono)' }}>
              ₹95,711.00
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              At ₹169.40 direct loss per RTO
            </div>
          </div>
        </div>
      </div>

      {/* 4 Finding Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(520px, 1fr))', gap: '24px' }}>
        {/* Finding 1 */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Users size={18} color="#10b981" />
              Finding 1: Prior RTO History Escalation (3.22x Multiplier)
            </div>
            <span className="badge badge-cancel">Strongest Signal</span>
          </div>

          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px', lineHeight: 1.5 }}>
            Customers with even 1 prior RTO experience a massive return rate of <strong>45.07%</strong>, compared to 
            only <strong>14.00%</strong> for clean repeat customers. Repeat clean history is the single highest trust signal.
          </p>

          <div style={{ height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={finding1Data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27354f" />
                <XAxis dataKey="segment" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} unit="%" />
                <Tooltip contentStyle={{ backgroundColor: '#172033', borderColor: '#27354f', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="rto_rate" name="RTO Rate %" radius={[4, 4, 0, 0]}>
                  {finding1Data.map((entry, index) => (
                    <Bar key={`bar-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Finding 2 */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <MapPin size={18} color="#3b82f6" />
              Finding 2: Address Completeness & Defectiveness
            </div>
            <span className="badge badge-ship-as-is">NLP Impact</span>
          </div>

          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px', lineHeight: 1.5 }}>
            Short, generic, or placeholder addresses (e.g., "xyz", "home", or &lt;20 characters) suffer an alarming 
            <strong> 61.75% RTO rate</strong>. Well-structured addresses containing specific house/flat numbers drop RTO to <strong>23.94%</strong>.
          </p>

          <div style={{ height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={finding2Data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27354f" />
                <XAxis dataKey="tier" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} unit="%" />
                <Tooltip contentStyle={{ backgroundColor: '#172033', borderColor: '#27354f', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="rto_rate" name="RTO Rate %" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Finding 3 */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <AlertTriangle size={18} color="#f59e0b" />
              Finding 3: Test Names & Rapid Duplicate Reorders
            </div>
            <span className="badge badge-confirm">Fraud Prevention</span>
          </div>

          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px', lineHeight: 1.5 }}>
            Orders with test names ("Test Order", "asdf", "qwerty") exhibit a <strong>63.64% RTO rate</strong>. Furthermore, 
            we identified 28 orders placed within 15 minutes of an existing order by the same phone number (including 25 rapid orders in the <code>KT15xxxx</code> series).
          </p>

          <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '16px', borderRadius: 'var(--radius-md)', fontSize: '13px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span>Suspicious Test Names RTO Rate:</span>
              <strong style={{ color: '#f43f5e', fontFamily: 'var(--font-mono)' }}>63.64% (44 orders)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span>Rapid Reorder Burst RTO Rate:</span>
              <strong style={{ color: '#f43f5e', fontFamily: 'var(--font-mono)' }}>57.14% (28 orders)</strong>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px', lineHeight: 1.4 }}>
              Recommendation: Automatic debounce timer in Shopify checkout to deduplicate impulse multiple clicks before dispatch.
            </div>
          </div>
        </div>

        {/* Finding 4 */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Truck size={18} color="#8b5cf6" />
              Finding 4: Courier Efficiency & Channel Disparities
            </div>
            <span className="badge badge-prepaid">Routing Optimization</span>
          </div>

          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px', lineHeight: 1.5 }}>
            Delhivery achieves the lowest COD RTO rate at <strong>26.04%</strong>, while Xpressbees experiences the highest at <strong>30.95%</strong>.
            Paid social (Meta Ads) accounts for 38.6% of order volume with elevated <strong>31.24% RTO</strong>.
          </p>

          <div style={{ height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={courierData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27354f" />
                <XAxis dataKey="courier" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} unit="%" />
                <Tooltip contentStyle={{ backgroundColor: '#172033', borderColor: '#27354f', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="rto_rate" name="RTO Rate %" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

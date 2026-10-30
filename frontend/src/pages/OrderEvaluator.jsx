import React, { useState } from 'react';
import { 
  SearchCode, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldAlert, 
  ArrowRight, 
  DollarSign, 
  MessageSquare,
  Zap,
  Info,
  Copy,
  Check
} from 'lucide-react';
import { evaluateOrder } from '../services/api';

const PRESETS = [
  {
    name: 'Clean Repeat Customer',
    tag: 'Safe (0% RTO)',
    color: '#10b981',
    data: {
      order_id: 'PRESET_CLEAN_01',
      customer_name: 'Priya Sharma',
      phone: '9820112345',
      address: 'Flat 402, Sunshine Heights, 12th Main, Indiranagar',
      city: 'Bengaluru',
      state: 'Karnataka',
      pincode: '560038',
      order_value: 649,
      customer_prior_orders: 3,
      customer_prior_rto: 0,
      utm_source: 'direct',
      courier: 'Delhivery'
    }
  },
  {
    name: 'First-Time Meta Shopper',
    tag: 'Moderate Risk',
    color: '#3b82f6',
    data: {
      order_id: 'PRESET_CONFIRM_01',
      customer_name: 'Rahul Verma',
      phone: '9811223344',
      address: 'House 12, Sector 15, Near City Hospital',
      city: 'Gurgaon',
      state: 'Haryana',
      pincode: '122001',
      order_value: 649,
      customer_prior_orders: 0,
      customer_prior_rto: 0,
      utm_source: 'meta',
      courier: 'Delhivery'
    }
  },
  {
    name: 'High AOV Meta Order',
    tag: 'Prepaid Nudge',
    color: '#8b5cf6',
    data: {
      order_id: 'PRESET_PREPAID_01',
      customer_name: 'Aman Patel',
      phone: '9909887766',
      address: 'Shop 4, Station Road, Near Railway Circle',
      city: 'Ahmedabad',
      state: 'Gujarat',
      pincode: '380001',
      order_value: 1499,
      customer_prior_orders: 0,
      customer_prior_rto: 0,
      utm_source: 'meta',
      courier: 'Shadowfax'
    }
  },
  {
    name: 'Defective Address ("xyz")',
    tag: 'Hold / Cancel',
    color: '#f43f5e',
    data: {
      order_id: 'PRESET_DEFECT_01',
      customer_name: 'Vikram Singh',
      phone: '9123456789',
      address: 'xyz',
      city: 'Delhi',
      state: 'Delhi',
      pincode: '110001',
      order_value: 649,
      customer_prior_orders: 0,
      customer_prior_rto: 0,
      utm_source: 'meta',
      courier: 'Delhivery'
    }
  },
  {
    name: 'Hinglish Landmark Address',
    tag: 'Local Landmark',
    color: '#10b981',
    data: {
      order_id: 'PRESET_HINGLISH_01',
      customer_name: 'Rohan Gupta',
      phone: '9788776655',
      address: 'Makan No 44, Gali No 2, Peepal ke ped ke samne, Doodh dairy ke pass',
      city: 'Jaipur',
      state: 'Rajasthan',
      pincode: '302001',
      order_value: 649,
      customer_prior_orders: 0,
      customer_prior_rto: 0,
      utm_source: 'direct',
      courier: 'Delhivery'
    }
  },
  {
    name: 'Chronic RTO Abuser',
    tag: 'RTO Risk (75%)',
    color: '#f43f5e',
    data: {
      order_id: 'PRESET_ABUSER_01',
      customer_name: 'Suresh Raina',
      phone: '9455667788',
      address: 'Plot 54, Gandhi Nagar Colony',
      city: 'Lucknow',
      state: 'Uttar Pradesh',
      pincode: '226001',
      order_value: 649,
      customer_prior_orders: 4,
      customer_prior_rto: 3,
      utm_source: 'meta',
      courier: 'Delhivery'
    }
  }
];

export default function OrderEvaluator({ onSwitchToWhatsApp }) {
  const [formData, setFormData] = useState(PRESETS[0].data);
  const [result, setResult] = useState(null);
  const [evaluating, setEvaluating] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: (name === 'order_value' || name === 'customer_prior_orders' || name === 'customer_prior_rto')
        ? Number(value)
        : value
    }));
  };

  const handleLoadPreset = (preset) => {
    setFormData(preset.data);
    setResult(null);
  };

  const handleEvaluate = async (e) => {
    if (e) e.preventDefault();
    setEvaluating(true);
    try {
      const res = await evaluateOrder(formData);
      setResult(res.data);
    } catch (err) {
      console.error("Evaluation error:", err);
      alert("Failed to evaluate order. Please verify inputs.");
    } finally {
      setEvaluating(false);
    }
  };

  const handleCopyJson = () => {
    if (!result) return;
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const getActionBadgeClass = (action) => {
    switch (action) {
      case 'SHIP_AS_IS': return 'badge-ship-as-is';
      case 'SHIP_AFTER_CONFIRMATION': return 'badge-confirm';
      case 'NUDGE_TO_PREPAID': return 'badge-prepaid';
      case 'HOLD_OR_CANCEL': return 'badge-cancel';
      default: return 'badge-ship-as-is';
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '26px', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '10px' }}>
          Live Order Risk Evaluator & Decision Engine
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
          Real-time COD order risk scoring, NLP address classification, and explainable multi-factor audit log.
        </p>
      </div>

      {/* Preset Buttons */}
      <div className="card" style={{ marginBottom: '24px', padding: '16px 22px' }}>
        <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Zap size={14} color="#f59e0b" /> Select Scenario Preset
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {PRESETS.map((preset, idx) => (
            <button
              key={idx}
              className="btn btn-secondary"
              style={{ fontSize: '12.5px', padding: '8px 14px', borderRadius: 'var(--radius-sm)' }}
              onClick={() => handleLoadPreset(preset)}
            >
              <span style={{ 
                width: '8px', 
                height: '8px', 
                borderRadius: '50%', 
                backgroundColor: preset.color 
              }} />
              <span>{preset.name}</span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>({preset.tag})</span>
            </button>
          ))}
        </div>
      </div>

      {/* Form + Result Split */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '28px' }}>
        {/* Order Input Form */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <SearchCode size={18} color="var(--accent-blue)" />
              Order Parameters
            </div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Shopify COD Webhook Payload</span>
          </div>

          <form onSubmit={handleEvaluate}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              <div className="form-group">
                <label className="form-label">Order ID</label>
                <input 
                  type="text" 
                  name="order_id" 
                  className="form-control" 
                  value={formData.order_id} 
                  onChange={handleInputChange} 
                  required 
                />
              </div>

              <div className="form-group">
                <label className="form-label">Customer Name</label>
                <input 
                  type="text" 
                  name="customer_name" 
                  className="form-control" 
                  value={formData.customer_name} 
                  onChange={handleInputChange} 
                  required 
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Shipping Address</label>
              <textarea 
                name="address" 
                rows="2" 
                className="form-control" 
                value={formData.address} 
                onChange={handleInputChange} 
                required 
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
              <div className="form-group">
                <label className="form-label">City</label>
                <input 
                  type="text" 
                  name="city" 
                  className="form-control" 
                  value={formData.city} 
                  onChange={handleInputChange} 
                />
              </div>

              <div className="form-group">
                <label className="form-label">State</label>
                <input 
                  type="text" 
                  name="state" 
                  className="form-control" 
                  value={formData.state} 
                  onChange={handleInputChange} 
                />
              </div>

              <div className="form-group">
                <label className="form-label">Pincode</label>
                <input 
                  type="text" 
                  name="pincode" 
                  className="form-control" 
                  value={formData.pincode} 
                  onChange={handleInputChange} 
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
              <div className="form-group">
                <label className="form-label">Order Value (₹)</label>
                <input 
                  type="number" 
                  name="order_value" 
                  className="form-control" 
                  value={formData.order_value} 
                  onChange={handleInputChange} 
                />
              </div>

              <div className="form-group">
                <label className="form-label">Prior Orders</label>
                <input 
                  type="number" 
                  name="customer_prior_orders" 
                  className="form-control" 
                  value={formData.customer_prior_orders} 
                  onChange={handleInputChange} 
                />
              </div>

              <div className="form-group">
                <label className="form-label">Prior RTO Count</label>
                <input 
                  type="number" 
                  name="customer_prior_rto" 
                  className="form-control" 
                  value={formData.customer_prior_rto} 
                  onChange={handleInputChange} 
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '22px' }}>
              <div className="form-group">
                <label className="form-label">Acquisition Channel (UTM)</label>
                <select 
                  name="utm_source" 
                  className="form-control" 
                  value={formData.utm_source} 
                  onChange={handleInputChange}
                >
                  <option value="direct">Direct / Organic</option>
                  <option value="meta">Meta Ads (Facebook/Instagram)</option>
                  <option value="google">Google Search</option>
                  <option value="influencer">Influencer Campaign</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Courier Partner</label>
                <select 
                  name="courier" 
                  className="form-control" 
                  value={formData.courier} 
                  onChange={handleInputChange}
                >
                  <option value="Delhivery">Delhivery</option>
                  <option value="Shadowfax">Shadowfax</option>
                  <option value="Bluedart">Bluedart</option>
                  <option value="Xpressbees">Xpressbees</option>
                </select>
              </div>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary" 
              style={{ width: '100%', padding: '13px', fontSize: '14px' }}
              disabled={evaluating}
            >
              <Sparkles size={16} />
              {evaluating ? 'Evaluating Multi-Factor Risk...' : 'Run Decision Engine'}
            </button>
          </form>
        </div>

        {/* Evaluation Output Card */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <ShieldAlert size={18} color="var(--accent-purple)" />
              Decision Engine Output
            </div>
            {result && (
              <div style={{ display: 'flex', gap: '8px' }}>
                <button 
                  className="btn btn-secondary" 
                  style={{ padding: '4px 10px', fontSize: '11px' }}
                  onClick={handleCopyJson}
                  title="Copy JSON Payload"
                >
                  {copied ? <Check size={12} color="#10b981" /> : <Copy size={12} />}
                  {copied ? 'Copied' : 'JSON'}
                </button>
                <span className="badge" style={{ backgroundColor: 'rgba(255, 255, 255, 0.08)' }}>
                  {result.explanation_source}
                </span>
              </div>
            )}
          </div>

          {!result ? (
            <div style={{ textAlign: 'center', padding: '80px 20px', color: 'var(--text-muted)' }}>
              <SearchCode size={44} style={{ opacity: 0.25, marginBottom: '14px' }} />
              <p style={{ fontSize: '13.5px' }}>Click "Run Decision Engine" or pick a scenario preset above to inspect calibrated decisions.</p>
            </div>
          ) : (
            <div>
              {/* Action Banner */}
              <div style={{ 
                padding: '18px', 
                borderRadius: 'var(--radius-md)', 
                backgroundColor: 'rgba(13, 19, 34, 0.85)', 
                border: '1px solid var(--border-color)',
                marginBottom: '20px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 800 }}>
                    Assigned Action
                  </span>
                  <span className={`badge ${getActionBadgeClass(result.action)}`} style={{ fontSize: '13px', padding: '5px 14px' }}>
                    {result.action}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginBottom: '10px' }}>
                  <span style={{ fontSize: '32px', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>
                    {(result.risk_score * 100).toFixed(0)}%
                  </span>
                  <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                    Estimated RTO Probability ({result.risk_level} Risk Category)
                  </span>
                </div>

                {/* Multi-Zone Score Bar */}
                <div style={{ width: '100%', height: '8px', backgroundColor: '#1e293b', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ 
                    width: `${Math.min(100, result.risk_score * 100)}%`, 
                    height: '100%', 
                    backgroundColor: result.risk_score < 0.2 ? '#10b981' : (result.risk_score < 0.45 ? '#3b82f6' : (result.risk_score < 0.68 ? '#8b5cf6' : '#f43f5e')),
                    transition: 'width 0.4s ease'
                  }} />
                </div>
              </div>

              {/* Plain-English Reason */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Decision Rationale
                </div>
                <div style={{ fontSize: '13px', lineHeight: 1.55, color: 'var(--text-primary)', backgroundColor: 'rgba(255, 255, 255, 0.03)', padding: '12px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                  {result.reason}
                </div>
              </div>

              {/* Next Operational Step */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Recommended Operational Next Step
                </div>
                <div style={{ fontSize: '13px', color: '#60a5fa', fontWeight: 700 }}>
                  👉 {result.next_step}
                </div>
              </div>

              {/* Risk Factors */}
              <div style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Detected Risk Factors & Multipliers
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {result.risk_factors.map((factor, idx) => (
                    <div key={idx} style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center', 
                      backgroundColor: 'rgba(13, 19, 34, 0.7)', 
                      padding: '9px 12px', 
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '12px',
                      border: '1px solid rgba(255, 255, 255, 0.04)'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ 
                          width: '8px', 
                          height: '8px', 
                          borderRadius: '50%', 
                          backgroundColor: factor.impact === 'POSITIVE' ? '#10b981' : (factor.impact === 'NEGATIVE' ? '#f43f5e' : '#94a3b8') 
                        }} />
                        <strong>{factor.name}:</strong>
                        <span style={{ color: 'var(--text-secondary)' }}>{factor.description}</span>
                      </div>
                      <span style={{ 
                        fontFamily: 'var(--font-mono)', 
                        fontWeight: 700, 
                        color: factor.weight > 0 ? '#f43f5e' : (factor.weight < 0 ? '#10b981' : '#94a3b8') 
                      }}>
                        {factor.weight > 0 ? `+${(factor.weight * 100).toFixed(0)}%` : `${(factor.weight * 100).toFixed(0)}%`}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Financial Impact Breakdown */}
              {result.expected_financial_impact && (
                <div style={{ 
                  backgroundColor: 'rgba(16, 185, 129, 0.06)', 
                  border: '1px solid rgba(16, 185, 129, 0.25)', 
                  borderRadius: 'var(--radius-md)', 
                  padding: '16px',
                  marginBottom: '20px'
                }}>
                  <div style={{ fontSize: '11px', fontWeight: 800, color: '#34d399', textTransform: 'uppercase', marginBottom: '8px' }}>
                    Financial Unit Economics (Expected Values)
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '12px' }}>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Delivered Margin: </span>
                      <strong style={{ fontFamily: 'var(--font-mono)' }}>₹{result.expected_financial_impact.expected_delivered_margin?.toFixed(2)}</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Expected RTO Loss: </span>
                      <strong style={{ color: '#f87171', fontFamily: 'var(--font-mono)' }}>₹{result.expected_financial_impact.expected_rto_loss?.toFixed(2)}</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Net Expected Value: </span>
                      <strong style={{ color: '#60a5fa', fontFamily: 'var(--font-mono)' }}>₹{result.expected_financial_impact.net_expected_value?.toFixed(2)}</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Prevented RTO Savings: </span>
                      <strong style={{ color: '#34d399', fontFamily: 'var(--font-mono)' }}>+₹{result.expected_financial_impact.prevented_rto_savings?.toFixed(2)}</strong>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Button: Jump to WhatsApp Simulator */}
              {(result.action === 'SHIP_AFTER_CONFIRMATION' || result.action === 'NUDGE_TO_PREPAID') && onSwitchToWhatsApp && (
                <button 
                  className="btn btn-outline-blue" 
                  style={{ width: '100%', padding: '12px' }}
                  onClick={() => onSwitchToWhatsApp(formData.order_id, result.action === 'NUDGE_TO_PREPAID' ? 'PREPAID_NUDGE' : 'CONFIRMATION')}
                >
                  <MessageSquare size={16} />
                  Simulate WhatsApp Communication for this Order
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  Save, 
  RotateCcw, 
  DollarSign, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  HelpCircle 
} from 'lucide-react';
import { getSettings, updateSettings } from '../services/api';

export default function SettingsPanel() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const res = await getSettings();
      setSettings(res.data);
    } catch (err) {
      console.error("Settings fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSliderChange = (field, val) => {
    setSettings(prev => ({
      ...prev,
      [field]: parseFloat(val)
    }));
    setSaveSuccess(false);
    setErrorMsg('');
  };

  const handleInputChange = (field, val) => {
    setSettings(prev => ({
      ...prev,
      [field]: parseFloat(val) || 0
    }));
    setSaveSuccess(false);
    setErrorMsg('');
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (settings.threshold_low_risk > settings.threshold_medium_risk) {
      setErrorMsg("Low Risk threshold cannot be higher than Medium Risk threshold.");
      return;
    }
    if (settings.threshold_medium_risk > settings.threshold_high_risk) {
      setErrorMsg("Medium Risk threshold cannot be higher than High Risk threshold.");
      return;
    }

    setSaving(true);
    setErrorMsg('');
    try {
      const res = await updateSettings(settings);
      setSettings(res.data);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 4000);
    } catch (err) {
      console.error("Settings save error:", err);
      setErrorMsg(err.response?.data?.detail || "Failed to update settings.");
    } finally {
      setSaving(false);
    }
  };

  if (loading || !settings) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 0', color: 'var(--text-secondary)' }}>
        <p>Loading operational thresholds and financial settings...</p>
      </div>
    );
  }

  // Calculate live direct RTO loss
  const calculatedDirectRtoLoss = (
    settings.forward_shipping_cost +
    settings.return_shipping_cost +
    settings.packaging_handling_cost +
    (settings.damage_probability * settings.product_cost)
  ).toFixed(2);

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 800 }}>Decision Thresholds & Unit Economics</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
          Tune autonomous risk buckets, prepaid conversion discount margins, and unit economics without modifying code.
        </p>
      </div>

      {saveSuccess && (
        <div style={{ 
          backgroundColor: 'rgba(16, 185, 129, 0.15)', 
          border: '1px solid #10b981', 
          color: '#34d399', 
          padding: '12px 18px', 
          borderRadius: 'var(--radius-md)',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <CheckCircle2 size={18} />
          <strong>Settings Updated!</strong> Changes are active across the decision engine and SQLite database.
        </div>
      )}

      {errorMsg && (
        <div style={{ 
          backgroundColor: 'rgba(239, 68, 68, 0.15)', 
          border: '1px solid #ef4444', 
          color: '#f87171', 
          padding: '12px 18px', 
          borderRadius: 'var(--radius-md)',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <AlertTriangle size={18} />
          <span>{errorMsg}</span>
        </div>
      )}

      <form onSubmit={handleSave}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '24px', marginBottom: '24px' }}>
          {/* Decision Engine Thresholds Card */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <Sliders size={18} color="var(--accent-blue)" />
                COD Risk Classification Thresholds
              </div>
            </div>

            {/* Threshold 1: Low Risk */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label className="form-label">
                  Low Risk Cutoff: <strong>SHIP_AS_IS</strong> (≤ {(settings.threshold_low_risk * 100).toFixed(0)}%)
                </label>
                <span style={{ fontFamily: 'var(--font-mono)', color: '#10b981', fontWeight: 700 }}>
                  {settings.threshold_low_risk}
                </span>
              </div>
              <input 
                type="range" 
                min="0.05" 
                max="0.40" 
                step="0.01" 
                value={settings.threshold_low_risk}
                onChange={(e) => handleSliderChange('threshold_low_risk', e.target.value)}
                style={{ width: '100%', accentColor: '#10b981' }}
              />
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Orders at or below this score bypass confirmation and dispatch immediately.
              </div>
            </div>

            {/* Threshold 2: Medium Risk */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label className="form-label">
                  Medium Risk Cutoff: <strong>SHIP_AFTER_CONFIRMATION</strong> ({(settings.threshold_low_risk * 100).toFixed(0)}% – {(settings.threshold_medium_risk * 100).toFixed(0)}%)
                </label>
                <span style={{ fontFamily: 'var(--font-mono)', color: '#3b82f6', fontWeight: 700 }}>
                  {settings.threshold_medium_risk}
                </span>
              </div>
              <input 
                type="range" 
                min="0.20" 
                max="0.60" 
                step="0.01" 
                value={settings.threshold_medium_risk}
                onChange={(e) => handleSliderChange('threshold_medium_risk', e.target.value)}
                style={{ width: '100%', accentColor: '#3b82f6' }}
              />
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Orders in this band trigger WhatsApp verification before label generation.
              </div>
            </div>

            {/* Threshold 3: High Risk */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label className="form-label">
                  High Risk Cutoff: <strong>NUDGE_TO_PREPAID</strong> ({(settings.threshold_medium_risk * 100).toFixed(0)}% – {(settings.threshold_high_risk * 100).toFixed(0)}%)
                </label>
                <span style={{ fontFamily: 'var(--font-mono)', color: '#8b5cf6', fontWeight: 700 }}>
                  {settings.threshold_high_risk}
                </span>
              </div>
              <input 
                type="range" 
                min="0.45" 
                max="0.85" 
                step="0.01" 
                value={settings.threshold_high_risk}
                onChange={(e) => handleSliderChange('threshold_high_risk', e.target.value)}
                style={{ width: '100%', accentColor: '#8b5cf6' }}
              />
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Orders in this band receive instant discount offer to switch to UPI.
              </div>
            </div>

            {/* Threshold 4: Cancellation */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label className="form-label">
                  Cancellation Threshold: <strong>HOLD_OR_CANCEL</strong> (≥ {(settings.threshold_cancel_risk * 100).toFixed(0)}%)
                </label>
                <span style={{ fontFamily: 'var(--font-mono)', color: '#f43f5e', fontWeight: 700 }}>
                  {settings.threshold_cancel_risk}
                </span>
              </div>
              <input 
                type="range" 
                min="0.55" 
                max="0.95" 
                step="0.01" 
                value={settings.threshold_cancel_risk}
                onChange={(e) => handleSliderChange('threshold_cancel_risk', e.target.value)}
                style={{ width: '100%', accentColor: '#f43f5e' }}
              />
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Only orders above this threshold with fraudulent patterns or chronic returns are held.
              </div>
            </div>

            {/* Other operational params */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginTop: '10px' }}>
              <div className="form-group">
                <label className="form-label">Min Pincode Sample Size</label>
                <input 
                  type="number" 
                  className="form-control" 
                  value={settings.min_pincode_sample_size}
                  onChange={(e) => handleInputChange('min_pincode_sample_size', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Confirmation Timeout (Hours)</label>
                <input 
                  type="number" 
                  className="form-control" 
                  value={settings.confirmation_timeout_hours}
                  onChange={(e) => handleInputChange('confirmation_timeout_hours', e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Financial Assumptions & Economics Card */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <DollarSign size={18} color="#34d399" />
                Financial Assumptions & Direct RTO Formula
              </div>
            </div>

            {/* Direct RTO loss formula live banner */}
            <div style={{ 
              backgroundColor: 'rgba(16, 185, 129, 0.08)', 
              border: '1px solid rgba(16, 185, 129, 0.25)', 
              borderRadius: 'var(--radius-md)', 
              padding: '14px',
              marginBottom: '20px'
            }}>
              <div style={{ fontSize: '11px', fontWeight: 700, color: '#34d399', textTransform: 'uppercase', marginBottom: '4px' }}>
                Assignment Direct RTO Loss Formula
              </div>
              <div style={{ fontSize: '22px', fontWeight: 800, color: '#10b981', fontFamily: 'var(--font-mono)' }}>
                ₹{calculatedDirectRtoLoss}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                = ₹{settings.forward_shipping_cost} (Fwd) + ₹{settings.return_shipping_cost} (Ret) + ₹{settings.packaging_handling_cost} (Pack) + ({settings.damage_probability} × ₹{settings.product_cost} Damage)
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div className="form-group">
                <label className="form-label">Average Order Value (₹)</label>
                <input 
                  type="number" 
                  className="form-control" 
                  value={settings.default_aov}
                  onChange={(e) => handleInputChange('default_aov', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Delivered Gross Margin (%)</label>
                <input 
                  type="number" 
                  step="0.01" 
                  className="form-control" 
                  value={settings.gross_margin_pct}
                  onChange={(e) => handleInputChange('gross_margin_pct', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Forward Shipping Cost (₹)</label>
                <input 
                  type="number" 
                  className="form-control" 
                  value={settings.forward_shipping_cost}
                  onChange={(e) => handleInputChange('forward_shipping_cost', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Return Shipping Cost (₹)</label>
                <input 
                  type="number" 
                  className="form-control" 
                  value={settings.return_shipping_cost}
                  onChange={(e) => handleInputChange('return_shipping_cost', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Packaging & Handling (₹)</label>
                <input 
                  type="number" 
                  className="form-control" 
                  value={settings.packaging_handling_cost}
                  onChange={(e) => handleInputChange('packaging_handling_cost', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Damage Probability (0.0 - 1.0)</label>
                <input 
                  type="number" 
                  step="0.01" 
                  className="form-control" 
                  value={settings.damage_probability}
                  onChange={(e) => handleInputChange('damage_probability', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Product Cost (₹)</label>
                <input 
                  type="number" 
                  className="form-control" 
                  value={settings.product_cost}
                  onChange={(e) => handleInputChange('product_cost', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Customer Acquisition Cost (₹)</label>
                <input 
                  type="number" 
                  className="form-control" 
                  value={settings.cac}
                  onChange={(e) => handleInputChange('cac', e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
          <button 
            type="button" 
            className="btn btn-secondary" 
            onClick={fetchSettings}
            disabled={saving}
          >
            <RotateCcw size={16} /> Reset
          </button>
          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ padding: '10px 24px' }}
            disabled={saving}
          >
            <Save size={16} /> {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </form>
    </div>
  );
}

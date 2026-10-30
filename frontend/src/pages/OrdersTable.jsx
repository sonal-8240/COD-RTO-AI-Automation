import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  ChevronLeft, 
  ChevronRight, 
  X, 
  Eye, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  DollarSign, 
  MessageSquare,
  Sparkles,
  Download
} from 'lucide-react';
import { getOrders } from '../services/api';

export default function OrdersTable({ onOpenWhatsApp }) {
  const [orders, setOrders] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [courierFilter, setCourierFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, [page, actionFilter, riskFilter, courierFilter]);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const params = {
        page,
        page_size: pageSize,
        search: search || undefined,
        action: actionFilter || undefined,
        risk_level: riskFilter || undefined,
        courier: courierFilter || undefined
      };
      const res = await getOrders(params);
      setOrders(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error("Orders fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchOrders();
  };

  const getActionBadge = (action) => {
    switch (action) {
      case 'SHIP_AS_IS':
        return <span className="badge badge-ship-as-is">SHIP_AS_IS</span>;
      case 'SHIP_AFTER_CONFIRMATION':
        return <span className="badge badge-confirm">SHIP_AFTER_CONFIRMATION</span>;
      case 'NUDGE_TO_PREPAID':
        return <span className="badge badge-prepaid">NUDGE_TO_PREPAID</span>;
      case 'HOLD_OR_CANCEL':
        return <span className="badge badge-cancel">HOLD_OR_CANCEL</span>;
      default:
        return <span className="badge">{action || 'PENDING'}</span>;
    }
  };

  const getRiskBadge = (level, score) => {
    let colorClass = 'badge-low';
    if (level === 'MEDIUM') colorClass = 'badge-medium';
    if (level === 'HIGH') colorClass = 'badge-high';
    if (level === 'CRITICAL') colorClass = 'badge-critical';

    return (
      <span className={`badge ${colorClass}`} style={{ fontFamily: 'var(--font-mono)' }}>
        {score !== undefined ? `${(score * 100).toFixed(0)}%` : level}
      </span>
    );
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: 800 }}>Orders & Decision Registry</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
            Historical COD orders, individual AI decision rationales, and complete customer audit trail.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <div style={{ 
            backgroundColor: 'rgba(16, 185, 129, 0.1)', 
            border: '1px solid rgba(16, 185, 129, 0.3)', 
            padding: '6px 14px', 
            borderRadius: 'var(--radius-sm)',
            fontSize: '12px',
            color: '#34d399',
            fontWeight: 700
          }}>
            1,422 Delivered
          </div>
          <div style={{ 
            backgroundColor: 'rgba(244, 63, 94, 0.1)', 
            border: '1px solid rgba(244, 63, 94, 0.3)', 
            padding: '6px 14px', 
            borderRadius: 'var(--radius-sm)',
            fontSize: '12px',
            color: '#fb7185',
            fontWeight: 700
          }}>
            565 Baseline RTO
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="card" style={{ marginBottom: '20px', padding: '16px' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: '1 1 240px', position: 'relative' }}>
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 14, top: 13 }} />
            <input 
              type="text" 
              className="form-control" 
              placeholder="Search by Order ID, Customer Name, Pincode..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '38px', width: '100%' }}
            />
          </div>

          <select 
            className="form-control"
            value={actionFilter}
            onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
            style={{ width: '180px' }}
          >
            <option value="">All Actions</option>
            <option value="SHIP_AS_IS">SHIP_AS_IS</option>
            <option value="SHIP_AFTER_CONFIRMATION">SHIP_AFTER_CONFIRMATION</option>
            <option value="NUDGE_TO_PREPAID">NUDGE_TO_PREPAID</option>
            <option value="HOLD_OR_CANCEL">HOLD_OR_CANCEL</option>
          </select>

          <select 
            className="form-control"
            value={riskFilter}
            onChange={(e) => { setRiskFilter(e.target.value); setPage(1); }}
            style={{ width: '140px' }}
          >
            <option value="">All Risk Tiers</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>

          <select 
            className="form-control"
            value={courierFilter}
            onChange={(e) => { setCourierFilter(e.target.value); setPage(1); }}
            style={{ width: '140px' }}
          >
            <option value="">All Couriers</option>
            <option value="Delhivery">Delhivery</option>
            <option value="Shadowfax">Shadowfax</option>
            <option value="Bluedart">Bluedart</option>
            <option value="Xpressbees">Xpressbees</option>
          </select>

          <button type="submit" className="btn btn-secondary">
            Apply Filters
          </button>
        </form>
      </div>

      {/* Orders Table */}
      <div className="table-container">
        <table className="custom-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Customer</th>
              <th>Destination</th>
              <th>Amount</th>
              <th>Courier</th>
              <th>Actual Status</th>
              <th>AI Decision Action</th>
              <th>Risk Score</th>
              <th style={{ textAlign: 'right' }}>Audit</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '50px', color: 'var(--text-muted)' }}>
                  Loading orders...
                </td>
              </tr>
            ) : orders.length === 0 ? (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '50px', color: 'var(--text-muted)' }}>
                  No orders matching the specified filter criteria.
                </td>
              </tr>
            ) : (
              orders.map((o) => (
                <tr key={o.order_id}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#38bdf8' }}>
                    {o.order_id}
                  </td>
                  <td>
                    <div style={{ fontWeight: 700 }}>{o.customer_name}</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                      {o.phone || '—'}
                    </div>
                  </td>
                  <td>
                    <div>{o.city || 'Unknown'}, {o.pincode}</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {o.address}
                    </div>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 800 }}>
                    ₹{o.order_value?.toFixed(0)}
                  </td>
                  <td>
                    <span style={{ fontSize: '12px', color: '#cbd5e1' }}>{o.courier}</span>
                  </td>
                  <td>
                    <span style={{ 
                      fontWeight: 800, 
                      fontSize: '11px',
                      color: o.final_status === 'DELIVERED' ? '#34d399' : (o.final_status === 'RTO' ? '#f87171' : '#fbbf24') 
                    }}>
                      {o.final_status}
                    </span>
                  </td>
                  <td>
                    {getActionBadge(o.decision?.action)}
                  </td>
                  <td>
                    {getRiskBadge(o.decision?.risk_level, o.decision?.risk_score)}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button 
                      className="btn btn-secondary" 
                      style={{ padding: '6px 12px', fontSize: '11px', borderRadius: 'var(--radius-sm)' }}
                      onClick={() => setSelectedOrder(o)}
                    >
                      <Eye size={12} /> Inspect
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px' }}>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          Showing {orders.length} of {total.toLocaleString()} total orders (Page {page} of {totalPages})
        </span>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            className="btn btn-secondary" 
            style={{ padding: '6px 14px' }}
            disabled={page <= 1}
            onClick={() => setPage(p => Math.max(1, p - 1))}
          >
            <ChevronLeft size={16} /> Prev
          </button>
          <button 
            className="btn btn-secondary" 
            style={{ padding: '6px 14px' }}
            disabled={page >= totalPages}
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
          >
            Next <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Explainability Slide-Out Drawer */}
      {selectedOrder && (
        <div className="drawer-overlay" onClick={() => setSelectedOrder(null)}>
          <div className="drawer-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ fontSize: '20px', fontWeight: 800 }}>Order #{selectedOrder.order_id}</h2>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  Placed: {new Date(selectedOrder.order_datetime).toLocaleString()}
                </span>
              </div>
              <button 
                onClick={() => setSelectedOrder(null)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={22} />
              </button>
            </div>

            {/* Decision Overview */}
            <div style={{ 
              backgroundColor: 'var(--bg-card)', 
              padding: '18px', 
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 800 }}>
                  Assigned Action
                </span>
                {getActionBadge(selectedOrder.decision?.action)}
              </div>

              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '34px', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>
                  {((selectedOrder.decision?.risk_score || 0) * 100).toFixed(0)}%
                </span>
                <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  Estimated RTO Risk Probability
                </span>
              </div>

              <div style={{ fontSize: '13px', lineHeight: 1.55, marginTop: '8px', color: '#e2e8f0' }}>
                {selectedOrder.decision?.reason}
              </div>
            </div>

            {/* Customer Details */}
            <div>
              <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Customer & Shipping Profile
              </div>
              <div style={{ backgroundColor: 'var(--bg-card)', padding: '16px', borderRadius: 'var(--radius-sm)', fontSize: '13px', border: '1px solid var(--border-color)' }}>
                <div style={{ marginBottom: '6px' }}><strong>Name:</strong> {selectedOrder.customer_name}</div>
                <div style={{ marginBottom: '6px' }}><strong>Masked Phone:</strong> <span style={{ fontFamily: 'var(--font-mono)' }}>{selectedOrder.phone}</span></div>
                <div style={{ marginBottom: '6px' }}><strong>Address:</strong> {selectedOrder.address}</div>
                <div style={{ marginBottom: '6px' }}><strong>City/Pincode:</strong> {selectedOrder.city}, {selectedOrder.pincode}</div>
                <div style={{ marginBottom: '6px' }}><strong>Order Value:</strong> ₹{selectedOrder.order_value} ({selectedOrder.payment_method})</div>
                <div><strong>Prior History:</strong> {selectedOrder.customer_prior_orders} orders, {selectedOrder.customer_prior_rto} prior RTO(s)</div>
              </div>
            </div>

            {/* Risk Factors Breakdown */}
            <div>
              <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Evaluated Risk Factors
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {selectedOrder.decision?.risk_factors?.map((f, i) => (
                  <div key={i} style={{ 
                    backgroundColor: 'var(--bg-card)', 
                    padding: '10px 14px', 
                    borderRadius: 'var(--radius-sm)', 
                    fontSize: '12px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    border: '1px solid rgba(255, 255, 255, 0.04)'
                  }}>
                    <div>
                      <div style={{ fontWeight: 700 }}>{f.name}</div>
                      <div style={{ color: 'var(--text-muted)' }}>{f.description}</div>
                    </div>
                    <span style={{ 
                      fontFamily: 'var(--font-mono)', 
                      fontWeight: 700,
                      color: f.weight > 0 ? '#f43f5e' : (f.weight < 0 ? '#10b981' : '#94a3b8')
                    }}>
                      {f.weight > 0 ? `+${(f.weight * 100).toFixed(0)}%` : `${(f.weight * 100).toFixed(0)}%`}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Action Button */}
            {onOpenWhatsApp && (
              <button 
                className="btn btn-primary"
                style={{ padding: '12px' }}
                onClick={() => {
                  const wf = selectedOrder.decision?.action === 'NUDGE_TO_PREPAID' ? 'PREPAID_NUDGE' : 'CONFIRMATION';
                  onOpenWhatsApp(selectedOrder.order_id, wf);
                }}
              >
                <MessageSquare size={16} /> Open in WhatsApp Simulator
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

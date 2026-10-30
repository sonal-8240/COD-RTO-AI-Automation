import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageSquare, 
  Send, 
  Clock, 
  RotateCcw, 
  DollarSign, 
  CreditCard, 
  AlertCircle,
  ShieldCheck,
  Smartphone,
  Sparkles,
  ArrowRight,
  Phone,
  Video,
  MoreVertical,
  Paperclip,
  Smile,
  Mic,
  Wifi,
  BatteryCharging
} from 'lucide-react';
import { 
  startWhatsAppFlow, 
  replyWhatsApp, 
  advanceWhatsAppTime, 
  simulatePaymentSuccess 
} from '../services/api';

export default function WhatsAppSimulator({ initialOrderId, initialWorkflow }) {
  const [orderId, setOrderId] = useState(initialOrderId || 'KT100001');
  const [workflowType, setWorkflowType] = useState(initialWorkflow || 'CONFIRMATION');
  const [discountPct, setDiscountPct] = useState(8.0);
  const [conversation, setConversation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [inputText, setInputText] = useState('');
  const chatBottomRef = useRef(null);

  useEffect(() => {
    if (orderId) {
      handleStartFlow();
    }
  }, [workflowType]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation?.messages]);

  const handleStartFlow = async () => {
    setLoading(true);
    try {
      const res = await startWhatsAppFlow(orderId, workflowType, discountPct);
      setConversation(res.data);
    } catch (err) {
      console.error("Start WhatsApp error:", err);
      alert("Failed to initialize conversation. Make sure order exists in DB.");
    } finally {
      setLoading(false);
    }
  };

  const handleSendReply = async (textToSend) => {
    const text = textToSend || inputText;
    if (!text || !text.trim() || !conversation) return;

    try {
      const res = await replyWhatsApp(conversation.conversation_id, text);
      setConversation(prev => ({
        ...prev,
        current_state: res.data.current_state,
        messages: res.data.messages
      }));
      setInputText('');
    } catch (err) {
      console.error("Reply error:", err);
    }
  };

  const handleAdvanceTime = async (hours) => {
    if (!conversation) return;
    try {
      const res = await advanceWhatsAppTime(conversation.conversation_id, hours);
      setConversation(prev => ({
        ...prev,
        current_state: res.data.current_state,
        simulated_current_time: res.data.simulated_current_time,
        messages: res.data.messages
      }));
    } catch (err) {
      console.error("Advance time error:", err);
    }
  };

  const handleSimulatePayment = async () => {
    if (!conversation) return;
    try {
      const res = await simulatePaymentSuccess(conversation.conversation_id);
      setConversation(prev => ({
        ...prev,
        current_state: res.data.current_state,
        messages: res.data.messages
      }));
    } catch (err) {
      console.error("Payment error:", err);
    }
  };

  const getStateBadge = (state) => {
    switch (state) {
      case 'CONFIRMED':
        return <span className="badge badge-ship-as-is">✅ CONFIRMED (DISPATCH AUTHORIZED)</span>;
      case 'CANCELLED':
        return <span className="badge badge-cancel">🛑 CANCELLED (DISPATCH STOPPED)</span>;
      case 'TIMEOUT':
        return <span className="badge badge-cancel">⏰ TIMEOUT (AUTO-HELD 24H)</span>;
      case 'CONVERTED_PREPAID':
        return <span className="badge badge-prepaid">🎉 UPGRADED TO PREPAID (0% RTO)</span>;
      case 'OFFER_DECLINED':
        return <span className="badge badge-confirm">COD KEPT (DECLINED PREPAID)</span>;
      case 'AWAITING_PAYMENT':
        return <span className="badge badge-confirm">⏳ AWAITING ONLINE PAYMENT</span>;
      default:
        return <span className="badge badge-confirm">💬 AWAITING CUSTOMER REPLY</span>;
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '26px', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '10px' }}>
          Interactive WhatsApp Simulator
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
          Real-time smartphone simulator for 2-way confirmation (Workflow A) and instant prepaid nudge conversion (Workflow B).
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(340px, 420px) 1fr', gap: '32px', alignItems: 'start' }}>
        {/* Controls Deck */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Setup Card */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <Smartphone size={18} color="var(--accent-emerald)" />
                Workflow Configuration
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Order ID</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input 
                  type="text" 
                  className="form-control" 
                  value={orderId} 
                  onChange={(e) => setOrderId(e.target.value)} 
                  style={{ flex: 1, fontFamily: 'var(--font-mono)', fontWeight: 600 }}
                />
                <button className="btn btn-secondary" onClick={handleStartFlow} disabled={loading}>
                  Load
                </button>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Select Workflow</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  className={`btn ${workflowType === 'CONFIRMATION' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ flex: 1, fontSize: '12px', padding: '10px 8px' }}
                  onClick={() => setWorkflowType('CONFIRMATION')}
                >
                  Workflow A: Confirmation
                </button>
                <button
                  type="button"
                  className={`btn ${workflowType === 'PREPAID_NUDGE' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ flex: 1, fontSize: '12px', padding: '10px 8px' }}
                  onClick={() => setWorkflowType('PREPAID_NUDGE')}
                >
                  Workflow B: Prepaid Nudge
                </button>
              </div>
            </div>

            {workflowType === 'PREPAID_NUDGE' && (
              <div className="form-group" style={{ marginTop: '6px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <label className="form-label">Prepaid Discount Offer</label>
                  <strong style={{ color: '#c084fc', fontFamily: 'var(--font-mono)' }}>{discountPct}% OFF</strong>
                </div>
                <input 
                  type="range" 
                  min="5" 
                  max="15" 
                  step="1"
                  value={discountPct} 
                  onChange={(e) => setDiscountPct(Number(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--accent-purple)' }}
                />
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Drops RTO risk from 28% to 4%. High leverage on orders &gt;₹1,000.
                </div>
              </div>
            )}
          </div>

          {/* Quick Replies Deck */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <MessageSquare size={16} color="var(--accent-blue)" />
                Quick Customer Action Prompts
              </div>
            </div>

            {workflowType === 'CONFIRMATION' ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <button 
                  className="btn btn-secondary" 
                  style={{ justifyContent: 'flex-start', borderLeft: '4px solid #10b981', padding: '12px 14px' }}
                  onClick={() => handleSendReply("YES, please confirm my order")}
                >
                  <div>
                    <div style={{ fontWeight: 700, color: '#34d399' }}>Reply "YES"</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Confirms order & authorizes immediate courier dispatch</div>
                  </div>
                </button>

                <button 
                  className="btn btn-secondary" 
                  style={{ justifyContent: 'flex-start', borderLeft: '4px solid #f43f5e', padding: '12px 14px' }}
                  onClick={() => handleSendReply("NO, please cancel my order")}
                >
                  <div>
                    <div style={{ fontWeight: 700, color: '#fb7185' }}>Reply "NO"</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Cancels order; stops package dispatch & saves ₹169.40</div>
                  </div>
                </button>

                <button 
                  className="btn btn-secondary" 
                  style={{ justifyContent: 'flex-start', borderLeft: '4px solid #f59e0b', padding: '12px 14px' }}
                  onClick={() => handleSendReply("When will it reach? Call before sending")}
                >
                  <div>
                    <div style={{ fontWeight: 700, color: '#fbbf24' }}>Reply Ambiguous Question</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Triggers polite clarifying bot response</div>
                  </div>
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <button 
                  className="btn btn-secondary" 
                  style={{ justifyContent: 'flex-start', borderLeft: '4px solid #8b5cf6', padding: '12px 14px' }}
                  onClick={() => handleSendReply("PAY - send payment link")}
                >
                  <div>
                    <div style={{ fontWeight: 700, color: '#c084fc' }}>Reply "PAY"</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Requests secure one-click UPI checkout link</div>
                  </div>
                </button>

                <button 
                  className="btn btn-secondary" 
                  style={{ justifyContent: 'flex-start', borderLeft: '4px solid #94a3b8', padding: '12px 14px' }}
                  onClick={() => handleSendReply("KEEP - I prefer cash on delivery")}
                >
                  <div>
                    <div style={{ fontWeight: 700, color: '#cbd5e1' }}>Reply "KEEP"</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Declines discount and retains Cash on Delivery</div>
                  </div>
                </button>

                {conversation?.current_state === 'AWAITING_PAYMENT' && (
                  <button 
                    className="btn btn-primary" 
                    style={{ marginTop: '8px', padding: '12px', backgroundColor: '#8b5cf6', color: '#fff', fontSize: '13px' }}
                    onClick={handleSimulatePayment}
                  >
                    <CreditCard size={16} />
                    Simulate Successful UPI / Online Payment
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Time Progression Deck (Assignment Requirement) */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <Clock size={16} color="var(--accent-amber)" />
                SLA & Timeout Progression
              </div>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px', lineHeight: 1.45 }}>
              Advance the simulated clock. If 24 hours elapse without customer confirmation, dispatch is placed on hold.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
              <button className="btn btn-secondary" onClick={() => handleAdvanceTime(1)}>
                +1 Hour
              </button>
              <button className="btn btn-secondary" onClick={() => handleAdvanceTime(6)}>
                +6 Hours
              </button>
              <button 
                className="btn btn-secondary" 
                style={{ borderColor: 'rgba(244, 63, 94, 0.4)', color: '#f87171' }}
                onClick={() => handleAdvanceTime(25)}
              >
                +25h (Timeout)
              </button>
            </div>
          </div>
        </div>

        {/* WhatsApp Smartphone UI */}
        <div>
          {/* Live Status Header */}
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px' }}>
            {getStateBadge(conversation?.current_state)}
          </div>

          <div className="phone-outer-chassis">
            {/* Phone Notch & Status Bar */}
            <div className="phone-notch-area">
              <span>9:41</span>
              <div className="phone-dynamic-island" />
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Wifi size={13} />
                <span style={{ fontSize: '10px' }}>5G</span>
                <BatteryCharging size={14} />
              </div>
            </div>

            {/* Phone WhatsApp Header */}
            <div className="phone-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div className="phone-avatar">HC</div>
                <div>
                  <div style={{ fontSize: '13.5px', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    Haircare Store
                    <span style={{ color: '#25d366', fontSize: '11px' }}>✓</span>
                  </div>
                  <div style={{ fontSize: '10.5px', color: '#8696a0' }}>Official Business • online</div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '14px', color: '#aebac1' }}>
                <Video size={17} style={{ cursor: 'pointer' }} />
                <Phone size={15} style={{ cursor: 'pointer' }} />
                <MoreVertical size={16} style={{ cursor: 'pointer' }} />
              </div>
            </div>

            {/* Chat Body */}
            <div className="phone-chat-area">
              <div className="bubble-system">
                🔒 Messages and calls are end-to-end encrypted. SmartCOD AI Verified Merchant Account.
              </div>

              {conversation?.messages?.map((msg, index) => {
                const isBot = msg.sender === 'BOT';
                const isCustomer = msg.sender === 'CUSTOMER';
                const isSystem = msg.sender === 'SYSTEM';

                if (isSystem) {
                  return (
                    <div key={index} className="bubble-system">
                      {msg.text}
                    </div>
                  );
                }

                return (
                  <div key={index} className={`chat-bubble ${isBot ? 'bubble-bot' : 'bubble-customer'}`}>
                    <div style={{ whiteSpace: 'pre-line' }}>{msg.text}</div>
                    <div className="bubble-time">
                      <span>{msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '12:00'}</span>
                      {isCustomer && <span style={{ color: '#53bdeb' }}>✓✓</span>}
                    </div>
                  </div>
                );
              })}

              <div ref={chatBottomRef} />
            </div>

            {/* In-Phone Quick Suggestion Chips */}
            {conversation?.current_state === 'PENDING_REPLY' && (
              <div style={{ 
                backgroundColor: '#111b21', 
                padding: '6px 12px', 
                display: 'flex', 
                gap: '8px', 
                borderTop: '1px solid rgba(255, 255, 255, 0.05)',
                overflowX: 'auto'
              }}>
                {workflowType === 'CONFIRMATION' ? (
                  <>
                    <button 
                      onClick={() => handleSendReply("YES")}
                      style={{ 
                        background: '#005c4b', 
                        border: 'none', 
                        borderRadius: '16px', 
                        padding: '4px 12px', 
                        color: '#fff', 
                        fontSize: '11px', 
                        fontWeight: 700, 
                        cursor: 'pointer' 
                      }}
                    >
                      "YES" Confirm
                    </button>
                    <button 
                      onClick={() => handleSendReply("NO")}
                      style={{ 
                        background: '#202c33', 
                        border: '1px solid rgba(244, 63, 94, 0.4)', 
                        borderRadius: '16px', 
                        padding: '4px 12px', 
                        color: '#f87171', 
                        fontSize: '11px', 
                        fontWeight: 700, 
                        cursor: 'pointer' 
                      }}
                    >
                      "NO" Cancel
                    </button>
                  </>
                ) : (
                  <>
                    <button 
                      onClick={() => handleSendReply("PAY")}
                      style={{ 
                        background: '#8b5cf6', 
                        border: 'none', 
                        borderRadius: '16px', 
                        padding: '4px 12px', 
                        color: '#fff', 
                        fontSize: '11px', 
                        fontWeight: 700, 
                        cursor: 'pointer' 
                      }}
                    >
                      "PAY" Link
                    </button>
                    <button 
                      onClick={() => handleSendReply("KEEP")}
                      style={{ 
                        background: '#202c33', 
                        border: 'none', 
                        borderRadius: '16px', 
                        padding: '4px 12px', 
                        color: '#e9edef', 
                        fontSize: '11px', 
                        fontWeight: 700, 
                        cursor: 'pointer' 
                      }}
                    >
                      "KEEP" COD
                    </button>
                  </>
                )}
              </div>
            )}

            {/* Phone Footer Input */}
            <div className="phone-footer">
              <Smile size={19} color="#8696a0" style={{ cursor: 'pointer' }} />
              <Paperclip size={18} color="#8696a0" style={{ cursor: 'pointer' }} />
              <input 
                type="text" 
                placeholder="Message"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendReply()}
                style={{
                  flex: 1,
                  backgroundColor: '#2a3942',
                  border: 'none',
                  borderRadius: '20px',
                  padding: '9px 14px',
                  color: '#fff',
                  fontSize: '12.5px',
                  outline: 'none'
                }}
              />
              {inputText.trim() ? (
                <button 
                  onClick={() => handleSendReply()}
                  style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '50%',
                    backgroundColor: '#00a884',
                    border: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    cursor: 'pointer'
                  }}
                >
                  <Send size={15} />
                </button>
              ) : (
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '50%',
                  backgroundColor: '#00a884',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff'
                }}>
                  <Mic size={16} />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

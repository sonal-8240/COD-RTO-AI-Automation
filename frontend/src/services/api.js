import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = () => api.get('/health');

export const getDashboardSummary = (dateFilter = 'all') =>
  api.get(`/dashboard/summary?date_filter=${dateFilter}`);

export const getOrders = (params = {}) =>
  api.get('/orders', { params });

export const getOrderById = (orderId) =>
  api.get(`/orders/${orderId}`);

export const evaluateOrder = (orderData) =>
  api.post('/orders/evaluate', orderData);

export const createOrder = (orderData) =>
  api.post('/orders', orderData);

export const getSettings = () =>
  api.get('/settings');

export const updateSettings = (settingsData) =>
  api.put('/settings', settingsData);

export const startWhatsAppFlow = (orderId, workflowType = 'CONFIRMATION', discountPct = 8.0) =>
  api.post('/whatsapp/start', {
    order_id: orderId,
    workflow_type: workflowType,
    discount_pct: discountPct
  });

export const getWhatsAppConversation = (conversationId) =>
  api.get(`/whatsapp/${conversationId}`);

export const replyWhatsApp = (conversationId, text) =>
  api.post(`/whatsapp/${conversationId}/reply`, { text });

export const advanceWhatsAppTime = (conversationId, hours = 1) =>
  api.post(`/whatsapp/${conversationId}/advance-time`, { hours });

export const simulatePaymentSuccess = (conversationId) =>
  api.post(`/whatsapp/${conversationId}/simulate-payment`, {});

export const getAnalysisFindings = () =>
  api.get('/analysis/findings');

export default api;

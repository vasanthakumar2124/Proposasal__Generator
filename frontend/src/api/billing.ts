import apiClient from './client'

export const billingApi = {
  getPlans: () => apiClient.get('/billing/plans'),

  getSubscription: () => apiClient.get('/billing/subscription'),

  createCheckout: (planId: string, interval: 'month' | 'year') =>
    apiClient.post('/billing/checkout', { plan_id: planId, interval }),

  cancelSubscription: () => apiClient.post('/billing/cancel'),

  getPortalUrl: () => apiClient.post('/billing/portal', { return_url: window.location.origin + '/billing' }),

  getUsage: () => apiClient.get('/billing/usage'),
}

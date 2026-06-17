import api from '../utils/api';

const dashboardService = {
  /** Fetch aggregated stats + recent trips for a user. */
  getStats: (userId) => api.get(`/dashboard/api/stats/${userId}/`),
  health: () => api.get('/dashboard/api/health/'),
};

export default dashboardService;

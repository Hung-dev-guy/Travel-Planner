import api from '../utils/api';

const tripService = {
  /**
   * Run the full AI trip-planning pipeline.
   * Returns { trip_overview, scheduling, validation, status_message }
   */
  generatePlan: (payload) => api.post('/workflow/api/run', payload),

  /** Save the generated trip to the database */
  savePlan: (payload) => api.post('/workflow/api/save-trip', payload),

  /** Fetch a saved trip by ID */
  getTripById: (tripId) => api.get(`/workflow/api/trip/${tripId}/`),

  /** Delete a saved trip */
  deleteTrip: (tripId) => api.delete(`/workflow/api/trip/${tripId}/delete`),

  /** Quick health-check to verify the Django server is reachable. */
  health: () => api.get('/workflow/api/health'),
};

export default tripService;

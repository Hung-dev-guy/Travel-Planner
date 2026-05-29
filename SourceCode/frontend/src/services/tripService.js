import api from '../utils/api';

const tripService = {
  createTrip:   (data) => api.post('/trips', data),
  getTrips:     ()     => api.get('/trips'),

  /**
   * Run the full planning pipeline.
   * @param {{
   *   user_des_input: string,
   *   destination: string,
   *   start_date: string,
   *   end_date: string,
   *   group_size: number,
   *   budget: number,
   *   travel_style: string[],
   *   travel_pace: string,
   *   companion_type: string,
   *   accommodation_style: string,
   *   health_limitations: string[]
   * }} payload
   */
  generatePlan: (payload) => api.post('/pipeline/run', payload),

  /** Quick health check to verify the Django server is reachable. */
  health:       ()       => api.get('/pipeline/health'),
};

export default tripService;

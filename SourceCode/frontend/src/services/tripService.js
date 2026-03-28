import api from '../utils/api';

const tripService = {
  createTrip: (data) => api.post('/trips', data),
  getTrips: () => api.get('/trips'),
};

export default tripService;

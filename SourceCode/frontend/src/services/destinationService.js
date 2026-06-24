import api from '../utils/api';

const destinationService = {
  /** Fetch destinations/locations, optionally filtered by category and search query */
  getLocations: (category = 'All', searchQuery = '') => {
    return api.get('/destinations/api/locations/', {
      params: {
        category,
        q: searchQuery
      }
    });
  },
  
  addLocation: (data) => {
    return api.post('/destinations/api/locations/add/', data);
  },

  editLocation: (data) => {
    return api.post('/destinations/api/locations/edit/', data);
  },

  deleteLocation: (data) => {
    return api.post('/destinations/api/locations/delete/', data);
  },

  addTransport: (data) => {
    return api.post('/destinations/api/transport/add/', data);
  },

  addReview: (data) => {
    return api.post('/destinations/api/locations/review/', data);
  },

  getReviews: (locationId) => {
    return api.get('/destinations/api/locations/reviews/', { params: { locationId } });
  },

  getTripsByLocation: (locationName) => {
    return api.get('/destinations/api/locations/trips/', { params: { locationName } });
  },

  getProvinces: () => {
    return api.get('/destinations/api/provinces/');
  },

  getWards: (province) => {
    return api.get('/destinations/api/wards/', { params: { province } });
  }
};

export default destinationService;

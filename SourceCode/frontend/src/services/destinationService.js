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
  }
};

export default destinationService;

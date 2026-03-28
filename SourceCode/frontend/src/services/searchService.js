import api from '../utils/api';

const searchService = {
  search: (query) => api.get(`/search?q=${query}`),
};

export default searchService;

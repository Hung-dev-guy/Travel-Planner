import { useState } from 'react';
import searchService from '../services/searchService';

const useSearch = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const search = async (query) => {
    setLoading(true);
    try {
      const res = await searchService.search(query);
      setResults(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return { results, loading, search };
};

export default useSearch;

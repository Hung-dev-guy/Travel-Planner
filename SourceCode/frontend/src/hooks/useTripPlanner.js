import { useState } from 'react';
import tripService from '../services/tripService';

const useTripPlanner = () => {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(false);

  const createTrip = async (data) => {
      setLoading(true);
      try {
          await tripService.createTrip(data);
          // fetch again or update local state
      } catch (err) {
          console.error(err);
      } finally {
          setLoading(false);
      }
  };

  return { trips, loading, createTrip };
};

export default useTripPlanner;

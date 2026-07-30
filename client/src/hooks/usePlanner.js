import { useContext } from 'react';
import { TripContext } from '../context/TripContext';

export const usePlanner = () => {
  const context = useContext(TripContext);
  if (!context) {
    throw new Error('usePlanner must be used within a TripProvider');
  }
  return context;
};

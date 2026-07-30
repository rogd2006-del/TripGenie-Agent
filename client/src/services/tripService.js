import api from './api';

export const tripService = {
  async getHistory() {
    const res = await api.get('/trip/history');
    return res.data;
  },

  async getTripById(tripId) {
    const res = await api.get(`/trip/${tripId}`);
    return res.data;
  },

  async saveTrip(tripId) {
    const res = await api.post(`/trip/save/${tripId}`);
    return res.data;
  },

  async deleteTrip(tripId) {
    const res = await api.delete(`/trip/${tripId}`);
    return res.data;
  },

  getPdfDownloadUrl(tripId) {
    return `/api/v1/trip/${tripId}/pdf`;
  }
};

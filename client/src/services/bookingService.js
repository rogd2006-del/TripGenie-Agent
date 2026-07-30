import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const bookingService = {
  /**
   * Create a new confirmed booking with auto-selected hotel and transport
   */
  async createBooking(bookingData) {
    try {
      const res = await api.post('/api/v1/booking/create', bookingData);
      return res.data;
    } catch (err) {
      console.error('Error creating booking:', err);
      throw err;
    }
  },

  /**
   * Fetch booking details by ID
   */
  async getBooking(bookingId) {
    try {
      const res = await api.get(`/api/v1/booking/${bookingId}`);
      return res.data;
    } catch (err) {
      console.error('Error fetching booking:', err);
      throw err;
    }
  },

  /**
   * Process payment simulation for a booking
   */
  async processPayment(bookingId, paymentMethod = 'Credit Card / UPI') {
    try {
      const res = await api.post(`/api/v1/booking/${bookingId}/pay`, {
        payment_method: paymentMethod,
      });
      return res.data;
    } catch (err) {
      console.error('Error processing payment:', err);
      throw err;
    }
  },

  /**
   * PDF Download URLs
   */
  getTicketPdfUrl(bookingId) {
    return `${API_BASE_URL}/api/v1/booking/${bookingId}/pdf/ticket`;
  },

  getHotelVoucherPdfUrl(bookingId) {
    return `${API_BASE_URL}/api/v1/booking/${bookingId}/pdf/hotel-voucher`;
  },

  getPaymentReceiptPdfUrl(bookingId) {
    return `${API_BASE_URL}/api/v1/booking/${bookingId}/pdf/receipt`;
  },
};

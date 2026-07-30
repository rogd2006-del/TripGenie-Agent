import React, { useState, useEffect } from 'react';
import { X, CheckCircle, CreditCard, Download, ShieldCheck, Ticket, Building, Receipt, ArrowRight, Loader2, AlertTriangle, Check } from 'lucide-react';
import { bookingService } from '../../services/bookingService';

export const BookingModal = ({ isOpen, onClose, trip, selectedHotel: initialHotel, selectedTransport: initialTransport }) => {
  const [step, setStep] = useState('review'); // 'review' | 'booking_success' | 'payment' | 'paid'
  const [loading, setLoading] = useState(false);
  const [booking, setBooking] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('UPI / Credit Card');
  
  // Selected options state
  const [activeHotel, setActiveHotel] = useState(initialHotel || trip?.hotels?.[0] || null);
  const [activeTransport, setActiveTransport] = useState(initialTransport || trip?.transport?.options?.[0] || null);

  useEffect(() => {
    if (initialHotel) setActiveHotel(initialHotel);
    else if (trip?.hotels?.[0]) setActiveHotel(trip.hotels[0]);
  }, [initialHotel, trip]);

  useEffect(() => {
    if (initialTransport) setActiveTransport(initialTransport);
    else if (trip?.transport?.options?.[0]) setActiveTransport(trip.transport.options[0]);
  }, [initialTransport, trip]);

  if (!isOpen || !trip) return null;

  // Financial Calculations for Review
  const duration = trip.duration_days || 4;
  const maxBudget = trip.budget || 20000;

  const hotelNightly = activeHotel?.price_per_night || activeHotel?.price || 2500;
  const hotelCost = activeHotel ? hotelNightly * duration : 0;
  const transportCost = activeTransport ? (activeTransport.price || 1200) : 0;
  
  const foodCost = trip.budget_breakdown?.food_cost || (maxBudget * 0.25);
  const sightseeingCost = trip.budget_breakdown?.sightseeing_cost || (maxBudget * 0.12);
  
  const subtotal = hotelCost + transportCost + foodCost + sightseeingCost;
  const taxes = roundVal(subtotal * 0.05);
  const grandTotal = roundVal(subtotal + taxes);
  const remainingBudget = roundVal(maxBudget - grandTotal);
  const isBudgetExceeded = grandTotal > maxBudget;
  const canBook = activeHotel && activeTransport && !isBudgetExceeded;

  function roundVal(num) {
    return Math.round((num + Number.EPSILON) * 100) / 100;
  }

  // Handle Step 1 -> Step 2: Book Now
  const handleConfirmBooking = async () => {
    if (!canBook) return;
    setLoading(true);
    try {
      const data = await bookingService.createBooking({
        trip_id: trip._id || trip.id || 'demo-trip',
        destination: trip.destination,
        hotel: activeHotel,
        transport: activeTransport,
        duration_days: duration,
        food_cost: foodCost,
        sightseeing_cost: sightseeingCost,
        max_budget: maxBudget,
      });

      setBooking(data);
      setStep('booking_success');
    } catch (err) {
      console.error('Failed to create booking:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle Step 2 -> Step 3: Payment
  const handlePayNow = async () => {
    if (!booking) return;
    setLoading(true);
    try {
      const updated = await bookingService.processPayment(booking._id || booking.booking_id, paymentMethod);
      setBooking(updated);
      setStep('paid');
    } catch (err) {
      console.error('Payment failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-slate-800/60 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* LOADING STATE */}
        {loading && (
          <div className="py-16 text-center space-y-4">
            <Loader2 className="w-10 h-10 text-emerald-400 animate-spin mx-auto" />
            <p className="text-sm font-bold text-slate-300">
              {step === 'review' ? 'Securing your hotel & transport reservations in database...' : 'Processing secure payment gateway...'}
            </p>
          </div>
        )}

        {/* STEP 1: BOOKING REVIEW PAGE */}
        {!loading && step === 'review' && (
          <div className="space-y-6">
            
            {/* Header */}
            <div>
              <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
                Review Your Travel Booking
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Verify hotel, transport, and itemized budget totals before locking in your reservation.
              </p>
            </div>

            {/* Warning Alert if Budget Exceeded */}
            {isBudgetExceeded && (
              <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-4 rounded-2xl text-xs flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
                <div>
                  <span className="font-bold block">Your booking exceeds the selected budget.</span>
                  <p className="text-[11px] text-rose-300/80 mt-0.5">
                    Grand Total (₹{grandTotal.toLocaleString('en-IN')}) is higher than your Maximum Budget (₹{maxBudget.toLocaleString('en-IN')}). Please select a cheaper hotel or transport option.
                  </p>
                </div>
              </div>
            )}

            {/* Selection Check Alert if missing options */}
            {(!activeHotel || !activeTransport) && (
              <div className="bg-amber-500/10 border border-amber-500/30 text-amber-400 p-4 rounded-2xl text-xs flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
                <div>
                  <span className="font-bold block">Missing Selection</span>
                  <p className="text-[11px] text-amber-300/80 mt-0.5">
                    Please select both a Hotel lodging option and a Transport commute option to proceed.
                  </p>
                </div>
              </div>
            )}

            {/* Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              
              {/* Selected Hotel */}
              <div className={`p-4 rounded-2xl border space-y-2 ${activeHotel ? 'bg-slate-950/70 border-slate-800' : 'bg-rose-950/20 border-rose-800'}`}>
                <div className="flex items-center justify-between text-emerald-400 font-bold border-b border-slate-800 pb-2">
                  <span className="flex items-center gap-1.5"><Building className="w-4 h-4" /> Selected Hotel</span>
                  {activeHotel && <Check className="w-4 h-4 text-emerald-400" />}
                </div>
                {activeHotel ? (
                  <>
                    <p className="font-bold text-white text-sm">{activeHotel.hotel_name || activeHotel.name}</p>
                    <p className="text-slate-400">{activeHotel.address}</p>
                    <div className="flex justify-between text-slate-300 pt-1 border-t border-slate-900">
                      <span>Rate ({duration} Nights):</span>
                      <span className="font-bold text-emerald-400">₹{hotelCost.toLocaleString('en-IN')}</span>
                    </div>
                  </>
                ) : (
                  <p className="text-rose-400 font-semibold py-2">No hotel selected. Please pick one from the hotel list.</p>
                )}
              </div>

              {/* Selected Transport */}
              <div className={`p-4 rounded-2xl border space-y-2 ${activeTransport ? 'bg-slate-950/70 border-slate-800' : 'bg-rose-950/20 border-rose-800'}`}>
                <div className="flex items-center justify-between text-cyan-400 font-bold border-b border-slate-800 pb-2">
                  <span className="flex items-center gap-1.5"><Ticket className="w-4 h-4" /> Selected Transport</span>
                  {activeTransport && <Check className="w-4 h-4 text-cyan-400" />}
                </div>
                {activeTransport ? (
                  <>
                    <p className="font-bold text-white text-sm">{activeTransport.operator_name}</p>
                    <p className="text-slate-400">{activeTransport.transport_type} • Vehicle: {activeTransport.vehicle_number}</p>
                    <div className="flex justify-between text-slate-300 pt-1 border-t border-slate-900">
                      <span>Ticket Price:</span>
                      <span className="font-bold text-cyan-400">₹{transportCost.toLocaleString('en-IN')}</span>
                    </div>
                  </>
                ) : (
                  <p className="text-rose-400 font-semibold py-2">No transport selected. Please pick one from transport choices.</p>
                )}
              </div>

            </div>

            {/* Financial Breakdown Table */}
            <div className="bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden text-xs">
              <div className="p-4 space-y-2.5">
                <div className="flex justify-between text-slate-300">
                  <span>Hotel Lodging ({duration} Nights)</span>
                  <span className="font-bold font-mono">₹{hotelCost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Transport Commute ({activeTransport?.transport_type || 'Commute'})</span>
                  <span className="font-bold font-mono">₹{transportCost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Curated Dining & Food</span>
                  <span className="font-bold font-mono">₹{foodCost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Sightseeing & Entry Fees</span>
                  <span className="font-bold font-mono">₹{sightseeingCost.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Taxes & Processing (5% GST)</span>
                  <span className="font-bold font-mono">₹{taxes.toLocaleString('en-IN')}</span>
                </div>
              </div>

              <div className="bg-slate-900 p-4 border-t border-slate-800 space-y-2">
                <div className="flex justify-between items-center text-sm">
                  <span className="font-extrabold text-white">Grand Total</span>
                  <span className={`text-xl font-extrabold font-mono ${isBudgetExceeded ? 'text-rose-400' : 'text-emerald-400'}`}>
                    ₹{grandTotal.toLocaleString('en-IN')}
                  </span>
                </div>

                <div className="flex justify-between items-center text-xs pt-2 border-t border-slate-800 text-slate-400">
                  <span>Maximum Budget: <strong className="text-slate-200">₹{maxBudget.toLocaleString('en-IN')}</strong></span>
                  <span>
                    Remaining Budget:{' '}
                    <strong className={remainingBudget < 0 ? 'text-rose-400' : 'text-emerald-400'}>
                      ₹{remainingBudget.toLocaleString('en-IN')}
                    </strong>
                  </span>
                </div>
              </div>
            </div>

            {/* Book Now Button Footer */}
            <div className="flex items-center justify-between pt-2">
              <button
                onClick={onClose}
                className="text-xs font-bold text-slate-400 hover:text-white"
              >
                Cancel
              </button>

              <button
                onClick={handleConfirmBooking}
                disabled={!canBook}
                className={`px-8 py-3.5 rounded-2xl font-extrabold text-xs shadow-xl transition-all flex items-center gap-2 ${
                  canBook
                    ? 'bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white shadow-emerald-500/25'
                    : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                }`}
              >
                <span>Book Now</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>

          </div>
        )}

        {/* STEP 2: BOOKING CONFIRMED SUCCESS PAGE */}
        {!loading && step === 'booking_success' && booking && (
          <div className="space-y-6">
            
            {/* Header */}
            <div className="text-center space-y-2">
              <div className="w-14 h-14 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mx-auto">
                <CheckCircle className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-extrabold text-white">Booking Confirmed & Saved!</h2>
              <p className="text-xs text-slate-400">
                Your reservation records have been stored in MongoDB with Confirmed status.
              </p>
            </div>

            {/* Reference IDs & Status */}
            <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Booking ID</span>
                <span className="font-extrabold text-emerald-400 font-mono">{booking.booking_id}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Hotel Booking ID</span>
                <span className="font-bold text-slate-200 font-mono">{booking.hotel_booking_id}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Transport ID</span>
                <span className="font-bold text-slate-200 font-mono">{booking.transport_booking_id}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Status</span>
                <span className="inline-block px-2.5 py-0.5 rounded-md bg-emerald-950 text-emerald-400 font-bold border border-emerald-800/60 text-[11px]">
                  {booking.status}
                </span>
              </div>
            </div>

            {/* Details Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              
              {/* Hotel */}
              <div className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 space-y-2">
                <div className="flex items-center gap-2 text-emerald-400 font-bold border-b border-slate-800 pb-2">
                  <Building className="w-4 h-4" /> Confirmed Hotel
                </div>
                <p className="font-bold text-white text-sm">{booking.hotel?.hotel_name || booking.hotel?.name}</p>
                <p className="text-slate-400">{booking.hotel?.address}</p>
                <div className="flex justify-between text-slate-300 pt-1">
                  <span>Nightly Rate:</span>
                  <span className="font-bold">₹{(booking.hotel?.price_per_night || booking.hotel?.price)?.toLocaleString('en-IN')}</span>
                </div>
              </div>

              {/* Transport */}
              <div className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 space-y-2">
                <div className="flex items-center gap-2 text-cyan-400 font-bold border-b border-slate-800 pb-2">
                  <Ticket className="w-4 h-4" /> Confirmed Transport
                </div>
                <p className="font-bold text-white text-sm">{booking.transport?.operator_name}</p>
                <p className="text-slate-400">
                  {booking.transport?.transport_type} • Vehicle: {booking.transport?.vehicle_number}
                </p>
                <div className="flex justify-between text-slate-300 pt-1">
                  <span>Departure:</span>
                  <span className="font-bold">{booking.transport?.departure_time}</span>
                </div>
              </div>

            </div>

            {/* Total Summary Bar */}
            <div className="bg-gradient-to-r from-slate-950 to-slate-900 p-4 rounded-2xl border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-400">Total Confirmed Price</span>
                <p className="text-xl font-extrabold text-emerald-400">
                  ₹{booking.grand_total?.toLocaleString('en-IN')}
                </p>
              </div>

              <button
                onClick={() => setStep('payment')}
                className="px-6 py-3 rounded-2xl bg-emerald-500 hover:bg-emerald-600 text-white font-extrabold text-xs shadow-xl shadow-emerald-500/25 transition-all flex items-center gap-2"
              >
                <span>Proceed to Payment</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>

          </div>
        )}

        {/* STEP 3: PAYMENT GATEWAY CHECKOUT */}
        {!loading && step === 'payment' && booking && (
          <div className="space-y-6">
            
            <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400 flex items-center justify-center">
                <CreditCard className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-xl font-extrabold text-white">Payment Simulation</h2>
                <p className="text-xs text-slate-400">Complete checkout for {booking.destination}</p>
              </div>
            </div>

            {/* Itemized Table */}
            <div className="bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden text-xs">
              <div className="p-4 space-y-3">
                <div className="flex justify-between text-slate-300">
                  <span>Hotel Accommodation ({booking.duration_days} Nights)</span>
                  <span className="font-bold font-mono">₹{booking.hotel_cost?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Transport Commute Ticket</span>
                  <span className="font-bold font-mono">₹{booking.transport_cost?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Curated Dining & Food</span>
                  <span className="font-bold font-mono">₹{booking.food_cost?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Sightseeing & Entry Passes</span>
                  <span className="font-bold font-mono">₹{booking.sightseeing_cost?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Taxes (5% GST)</span>
                  <span className="font-bold font-mono">₹{booking.taxes?.toLocaleString('en-IN')}</span>
                </div>
              </div>

              <div className="bg-slate-900/90 p-4 border-t border-slate-800 flex justify-between items-center text-sm">
                <span className="font-extrabold text-white">Grand Total Amount</span>
                <span className="text-xl font-extrabold text-emerald-400 font-mono">
                  ₹{booking.grand_total?.toLocaleString('en-IN')}
                </span>
              </div>
            </div>

            {/* Payment Method Selector */}
            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block">Simulated Payment Method</span>
              <div className="grid grid-cols-2 gap-3 text-xs">
                {['UPI / Instant Pay', 'Credit / Debit Card', 'Net Banking', 'TripGenie Wallet'].map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setPaymentMethod(m)}
                    className={`p-3 rounded-xl border text-left font-bold transition-all ${
                      paymentMethod === m
                        ? 'bg-purple-950/60 border-purple-500 text-white'
                        : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-2">
              <button
                onClick={() => setStep('booking_success')}
                className="text-xs font-bold text-slate-400 hover:text-white"
              >
                ← Back to Summary
              </button>

              <button
                onClick={handlePayNow}
                className="px-8 py-3.5 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-extrabold text-xs shadow-xl shadow-purple-600/25 transition-all flex items-center gap-2"
              >
                <CreditCard className="w-4 h-4" />
                <span>Pay Now (₹{booking.grand_total?.toLocaleString('en-IN')})</span>
              </button>
            </div>

          </div>
        )}

        {/* STEP 4: PAYMENT PAID & PDF DOWNLOADS */}
        {!loading && step === 'paid' && booking && (
          <div className="space-y-6">
            
            {/* Header */}
            <div className="text-center space-y-2">
              <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mx-auto shadow-xl shadow-emerald-500/10">
                <ShieldCheck className="w-10 h-10" />
              </div>
              <h2 className="text-2xl font-extrabold text-white">Payment Successful & Confirmed!</h2>
              <p className="text-xs text-emerald-400 font-mono font-bold">
                Payment Reference ID: {booking.payment_id}
              </p>
            </div>

            <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 flex justify-between items-center text-xs">
              <div>
                <span className="text-slate-400 block">Status</span>
                <span className="text-emerald-400 font-extrabold text-sm uppercase">PAID & CONFIRMED</span>
              </div>
              <div className="text-right">
                <span className="text-slate-400 block">Amount Paid</span>
                <span className="text-white font-extrabold text-sm font-mono">₹{booking.grand_total?.toLocaleString('en-IN')}</span>
              </div>
            </div>

            {/* PDF DOWNLOAD SECTION */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">Download Official Travel Documents</h3>
              
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                
                {/* PDF 1: Ticket */}
                <a
                  href={bookingService.getTicketPdfUrl(booking._id || booking.booking_id)}
                  download
                  className="p-4 rounded-2xl bg-slate-950 border border-slate-800 hover:border-cyan-500/50 transition-all flex flex-col items-center justify-center text-center space-y-2 group"
                >
                  <Ticket className="w-6 h-6 text-cyan-400 group-hover:scale-110 transition-transform" />
                  <span className="text-xs font-bold text-slate-200">Transport E-Ticket</span>
                  <span className="text-[10px] text-emerald-400 flex items-center gap-1 font-semibold">
                    <Download className="w-3 h-3" /> PDF Download
                  </span>
                </a>

                {/* PDF 2: Hotel Voucher */}
                <a
                  href={bookingService.getHotelVoucherPdfUrl(booking._id || booking.booking_id)}
                  download
                  className="p-4 rounded-2xl bg-slate-950 border border-slate-800 hover:border-emerald-500/50 transition-all flex flex-col items-center justify-center text-center space-y-2 group"
                >
                  <Building className="w-6 h-6 text-emerald-400 group-hover:scale-110 transition-transform" />
                  <span className="text-xs font-bold text-slate-200">Hotel Voucher</span>
                  <span className="text-[10px] text-emerald-400 flex items-center gap-1 font-semibold">
                    <Download className="w-3 h-3" /> PDF Download
                  </span>
                </a>

                {/* PDF 3: Payment Receipt */}
                <a
                  href={bookingService.getPaymentReceiptPdfUrl(booking._id || booking.booking_id)}
                  download
                  className="p-4 rounded-2xl bg-slate-950 border border-slate-800 hover:border-purple-500/50 transition-all flex flex-col items-center justify-center text-center space-y-2 group"
                >
                  <Receipt className="w-6 h-6 text-purple-400 group-hover:scale-110 transition-transform" />
                  <span className="text-xs font-bold text-slate-200">Payment Receipt</span>
                  <span className="text-[10px] text-emerald-400 flex items-center gap-1 font-semibold">
                    <Download className="w-3 h-3" /> PDF Download
                  </span>
                </a>

              </div>
            </div>

            {/* Done Button */}
            <div className="pt-2 text-center">
              <button
                onClick={onClose}
                className="px-8 py-3 rounded-2xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs transition-colors"
              >
                Close & Return to Itinerary
              </button>
            </div>

          </div>
        )}

      </div>
    </div>
  );
};


import mongoose from "mongoose";

const BookingSchema = new mongoose.Schema({
  customerName: String,
  numberOfGuests: Number,
  bookingDate: String,
  bookingTime: String,
  cuisinePreference: String,
  specialRequests: String,

  weatherInfo: Object,
  seatingPreference: String, // indoor / outdoor
  status: { type: String, default: "confirmed" },
  createdAt: { type: Date, default: Date.now },
});

export default mongoose.model("Booking", BookingSchema);

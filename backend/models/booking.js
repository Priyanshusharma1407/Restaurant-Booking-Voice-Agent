const mongoose = require("mongoose");

const BookingSchema = new mongoose.Schema(
  {
    customerName: { type: String, required: true },
    numberOfGuests: { type: Number, required: true },
    bookingDate: { type: String, required: true },
    bookingTime: { type: String, required: true },
    cuisinePreference: { type: String },
    specialRequests: { type: String },

    weatherInfo: {
      temp: { type: Number },
      description: { type: String },
    },

    seatingPreference: { type: String, default: "indoor" },
  },
  { timestamps: true }
);

module.exports = mongoose.model("Booking", BookingSchema);

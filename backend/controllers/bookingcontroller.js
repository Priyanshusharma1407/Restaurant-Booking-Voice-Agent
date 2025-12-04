import Booking from "../models/booking.js";
import { getWeatherForDate } from "../utils/weather.js";

// -----------------------------------------
// POST /api/bookings  ✔
// -----------------------------------------
export const createBooking = async (req, res) => {
  try {
    const {
      customerName,
      numberOfGuests,
      bookingDate,
      bookingTime,
      cuisinePreference,
      specialRequests,
      city,
    } = req.body;

    // Fetch weather
    const weather = await getWeatherForDate(city);

    // Seating logic
    let seating = "indoor";
    if (weather && weather.description.includes("clear")) {
      seating = "outdoor";
    }

    const booking = await Booking.create({
      customerName,
      numberOfGuests,
      bookingDate,
      bookingTime,
      cuisinePreference,
      specialRequests,
      weatherInfo: weather,
      seatingPreference: seating,
      status: "confirmed",
    });

    res.json(booking);
  } catch (err) {
    console.error("Error creating booking:", err);
    res.status(500).json({ error: "Server error" });
  }
};

// -----------------------------------------
// GET /api/bookings  ✔
// -----------------------------------------
export const getAllBookings = async (req, res) => {
  const bookings = await Booking.find().sort({ createdAt: -1 });
  res.json(bookings);
};

// -----------------------------------------
// GET /api/bookings/:id  ✔
// -----------------------------------------
export const getBookingById = async (req, res) => {
  try {
    const booking = await Booking.findById(req.params.id);

    if (!booking) {
      return res.status(404).json({ message: "Booking not found" });
    }

    res.json(booking);
  } catch (err) {
    res.status(400).json({ message: "Invalid booking ID" });
  }
};

// -----------------------------------------
// DELETE /api/bookings/:id  ✔
// -----------------------------------------
export const deleteBooking = async (req, res) => {
  try {
    const booking = await Booking.findByIdAndDelete(req.params.id);

    if (!booking) {
      return res.status(404).json({ message: "Booking not found" });
    }

    res.json({ message: "Booking deleted successfully" });
  } catch (err) {
    res.status(400).json({ message: "Invalid booking ID" });
  }
};

const Booking = require("../models/booking");
const { getWeatherForDate } = require("../utils/weather");

exports.createBooking = async (req, res) => {
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

    if (!customerName || !numberOfGuests || !bookingDate || !bookingTime) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    console.log("Creating booking for:", customerName, "City:", city);

    // Fetch Weather (Celsius + description)
    const weather = await getWeatherForDate(city);

    let tempC = null;
    let description = "unknown";
    let seatingPreference = "indoor";

    if (weather) {
      tempC = Math.round(weather.temp);
      description = weather.description;

      if (tempC >= 22 && description.includes("clear")) {
        seatingPreference = "outdoor";
      }
    }

    // Save to DB
    const newBooking = await Booking.create({
      customerName,
      numberOfGuests,
      bookingDate,
      bookingTime,
      cuisinePreference,
      specialRequests,
      weatherInfo: {
        temp: tempC,
        description,
      },
      seatingPreference,
    });

    console.log("Booking saved:", newBooking._id);

    res.json(newBooking);
  } catch (error) {
    console.error("Error creating booking:", error);
    res.status(500).json({ error: "Server error" });
  }
};

exports.getAllBookings = async (req, res) => {
  try {
    const bookings = await Booking.find().sort({ createdAt: -1 });
    res.json(bookings);
  } catch (error) {
    console.error("Error fetching bookings:", error);
    res.status(500).json({ error: "Server error" });
  }
};

exports.getBookingById = async (req, res) => {
  try {
    const booking = await Booking.findById(req.params.id);
    if (!booking) return res.status(404).json({ error: "Not found" });

    res.json(booking);
  } catch (error) {
    console.error("Error fetching booking:", error);
    res.status(500).json({ error: "Server error" });
  }
};

exports.deleteBooking = async (req, res) => {
  try {
    const deleted = await Booking.findByIdAndDelete(req.params.id);
    if (!deleted) return res.status(404).json({ error: "Not found" });

    res.json({ message: "Booking deleted" });
  } catch (error) {
    console.error("Error deleting booking:", error);
    res.status(500).json({ error: "Server error" });
  }
};

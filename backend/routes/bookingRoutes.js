import express from "express";
import {
  createBooking,
  getAllBookings,
  getBookingById,
  deleteBooking,
} from "../controllers/bookingcontroller.js";

const router = express.Router();

router.post("/", createBooking); // Create booking
router.get("/", getAllBookings); // Get all bookings
router.get("/:id", getBookingById); // Get booking by ID
router.delete("/:id", deleteBooking); // Delete booking by ID

export default router;

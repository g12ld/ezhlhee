"use strict";

const { handleBooking, handleError } = require("../server/booking-core.js");

module.exports = async function bookAppointment(req, res) {
  try {
    await handleBooking(req, res);
  } catch (error) {
    handleError(res, error);
  }
};

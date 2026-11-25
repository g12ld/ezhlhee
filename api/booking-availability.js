"use strict";

const { handleAvailability, handleError } = require("../server/booking-core.js");

module.exports = async function bookingAvailability(req, res) {
  try {
    await handleAvailability(req, res);
  } catch (error) {
    handleError(res, error);
  }
};

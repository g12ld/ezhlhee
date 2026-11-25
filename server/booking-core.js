"use strict";

const crypto = require("crypto");
const siteConfig = require("../data/site-config.js");

const RIYADH_OFFSET_MINUTES = 180;
const RATE_LIMIT_WINDOW_MS = 10 * 60 * 1000;
const availabilityBuckets = new Map();
const bookingBuckets = new Map();

class PublicBookingError extends Error {
  constructor(status, code, message, details = {}) {
    super(message);
    this.name = "PublicBookingError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

function sendJson(res, status, payload) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store, max-age=0");
  res.end(JSON.stringify(payload));
}

function handleError(res, error) {
  if (error instanceof PublicBookingError) {
    sendJson(res, error.status, {
      ok: false,
      code: error.code,
      message: error.message,
      ...error.details,
    });
    return;
  }

  console.error("booking_api_error", {
    name: error && error.name,
    message: error && error.message,
  });

  sendJson(res, 500, {
    ok: false,
    code: "server_error",
    message: "تعذر تنفيذ الطلب حالياً. حاول مرة أخرى أو تواصل معنا عبر واتساب.",
  });
}

function method(req, allowed) {
  if (!allowed.includes(req.method)) {
    throw new PublicBookingError(405, "method_not_allowed", "طريقة الطلب غير مدعومة.");
  }
}

function clientAddress(req) {
  const forwardedFor = String(req.headers["x-forwarded-for"] || "").split(",")[0].trim();
  return forwardedFor || req.socket?.remoteAddress || "unknown";
}

function rateLimitExceeded(bucket, key, max) {
  const now = Date.now();
  const current = bucket.get(key) || { count: 0, resetAt: now + RATE_LIMIT_WINDOW_MS };

  if (current.resetAt <= now) {
    bucket.set(key, { count: 1, resetAt: now + RATE_LIMIT_WINDOW_MS });
    return false;
  }

  current.count += 1;
  bucket.set(key, current);
  return current.count > max;
}

function cleanRateBuckets() {
  const now = Date.now();
  for (const [key, value] of availabilityBuckets.entries()) {
    if (value.resetAt <= now) availabilityBuckets.delete(key);
  }
  for (const [key, value] of bookingBuckets.entries()) {
    if (value.resetAt <= now) bookingBuckets.delete(key);
  }
}

function isSameOrigin(req) {
  const origin = req.headers.origin;
  if (!origin) return true;

  const host = req.headers["x-forwarded-host"] || req.headers.host;
  if (!host) return false;

  try {
    const originUrl = new URL(origin);
    return originUrl.host === host;
  } catch {
    return false;
  }
}

function readJsonBody(req, maxBytes = 16_384) {
  return new Promise((resolve, reject) => {
    let size = 0;
    let raw = "";

    req.on("data", (chunk) => {
      size += chunk.length;
      if (size > maxBytes) {
        reject(new PublicBookingError(413, "payload_too_large", "حجم الطلب أكبر من المسموح."));
        req.destroy();
        return;
      }
      raw += chunk;
    });

    req.on("end", () => {
      if (!raw) {
        reject(new PublicBookingError(400, "empty_payload", "بيانات الحجز غير مكتملة."));
        return;
      }

      try {
        resolve(JSON.parse(raw));
      } catch {
        reject(new PublicBookingError(400, "invalid_json", "صيغة الطلب غير صحيحة."));
      }
    });

    req.on("error", reject);
  });
}

function intEnv(name, fallback, min, max) {
  const value = Number.parseInt(process.env[name] || "", 10);
  if (Number.isNaN(value)) return fallback;
  return Math.min(Math.max(value, min), max);
}

function parseTime(value, fallback) {
  const raw = String(value || fallback || "").trim();
  const match = raw.match(/^([01]\d|2[0-3]):([0-5]\d)$/);
  if (!match) return parseTime(fallback, "10:00");
  return Number(match[1]) * 60 + Number(match[2]);
}

function parseWorkingDays(value, fallback) {
  const raw = String(value || "").trim();
  if (!raw) return fallback;

  const days = raw
    .split(",")
    .map((day) => Number.parseInt(day.trim(), 10))
    .filter((day) => Number.isInteger(day) && day >= 0 && day <= 6);

  return days.length ? [...new Set(days)] : fallback;
}

function bookingConfigFromEnv() {
  const defaults = siteConfig.booking || {};
  const timezone = process.env.BOOKING_TIMEZONE || defaults.timezone || "Asia/Riyadh";

  return {
    timezone: timezone === "Asia/Riyadh" ? timezone : "Asia/Riyadh",
    durationMinutes: intEnv("BOOKING_DURATION_MINUTES", defaults.durationMinutes || 30, 15, 180),
    bufferMinutes: intEnv("BOOKING_BUFFER_MINUTES", defaults.bufferMinutes || 0, 0, 120),
    minNoticeHours: intEnv("BOOKING_MIN_NOTICE_HOURS", defaults.minNoticeHours || 4, 0, 240),
    maxDaysAhead: intEnv("BOOKING_MAX_DAYS_AHEAD", defaults.maxDaysAhead || 21, 1, 90),
    workingDays: parseWorkingDays(
      process.env.BOOKING_WORKING_DAYS,
      defaults.workingDays || [0, 1, 2, 3, 4, 5, 6]
    ),
    startTimeMinutes: parseTime(process.env.BOOKING_START_TIME, defaults.startTime || "12:00"),
    endTimeMinutes: parseTime(process.env.BOOKING_END_TIME, defaults.endTime || "22:00"),
  };
}

function pad(value) {
  return String(value).padStart(2, "0");
}

function addDays(dateString, amount) {
  const [year, month, day] = dateString.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day + amount, 12, 0, 0));
  return date.toISOString().slice(0, 10);
}

function riyadhDateFromMs(ms) {
  return new Date(ms + RIYADH_OFFSET_MINUTES * 60_000).toISOString().slice(0, 10);
}

function riyadhDayOfWeek(dateString) {
  const [year, month, day] = dateString.split("-").map(Number);
  return new Date(Date.UTC(year, month - 1, day, 12, 0, 0)).getUTCDay();
}

function localRiyadhToUtcMs(dateString, minutes) {
  const [year, month, day] = dateString.split("-").map(Number);
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return Date.UTC(year, month - 1, day, hours, mins, 0) - RIYADH_OFFSET_MINUTES * 60_000;
}

function toRiyadhDateTime(dateString, minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${dateString}T${pad(hours)}:${pad(mins)}:00+03:00`;
}

function slotLabel(dateString, minutes) {
  return toRiyadhDateTime(dateString, minutes);
}

function formatArabicDate(dateString) {
  const [year, month, day] = dateString.split("-").map(Number);
  return new Intl.DateTimeFormat("ar-SA", {
    weekday: "long",
    month: "long",
    day: "numeric",
    timeZone: "Asia/Riyadh",
  }).format(new Date(Date.UTC(year, month - 1, day, 9, 0, 0)));
}

function formatArabicTime(minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return new Intl.DateTimeFormat("ar-SA", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
    timeZone: "Asia/Riyadh",
  }).format(new Date(Date.UTC(2024, 0, 1, hours - 3, mins, 0)));
}

function parseSlot(slot) {
  const match = String(slot || "").match(/^(\d{4}-\d{2}-\d{2})T([01]\d|2[0-3]):([0-5]\d):00\+03:00$/);
  if (!match) return null;

  const date = match[1];
  const minutes = Number(match[2]) * 60 + Number(match[3]);
  return {
    date,
    minutes,
    start: slotLabel(date, minutes),
    end: slotLabel(date, minutes + bookingConfigFromEnv().durationMinutes),
    startMs: localRiyadhToUtcMs(date, minutes),
  };
}

function generateCandidateSlots(daysAhead, config) {
  const today = riyadhDateFromMs(Date.now());
  const maxDays = Math.min(daysAhead, config.maxDaysAhead);
  const minStart = Date.now() + config.minNoticeHours * 60 * 60_000;
  const latestStart = Date.now() + config.maxDaysAhead * 24 * 60 * 60_000;
  const step = config.durationMinutes + config.bufferMinutes;
  const slots = [];

  for (let dayOffset = 0; dayOffset <= maxDays; dayOffset += 1) {
    const date = addDays(today, dayOffset);
    if (!config.workingDays.includes(riyadhDayOfWeek(date))) continue;

    for (
      let minutes = config.startTimeMinutes;
      minutes <= config.endTimeMinutes;
      minutes += step
    ) {
      const startMs = localRiyadhToUtcMs(date, minutes);
      if (startMs < minStart || startMs > latestStart) continue;

      slots.push({
        slot: slotLabel(date, minutes),
        date,
        dateLabel: formatArabicDate(date),
        timeLabel: formatArabicTime(minutes),
        start: slotLabel(date, minutes),
        end: slotLabel(date, minutes + config.durationMinutes),
        startMs,
        endMs: startMs + config.durationMinutes * 60_000,
      });
    }
  }

  return slots;
}

function overlaps(slot, busyItem) {
  const busyStart = Date.parse(busyItem.start);
  const busyEnd = Date.parse(busyItem.end);
  return Number.isFinite(busyStart) && Number.isFinite(busyEnd) && slot.startMs < busyEnd && slot.endMs > busyStart;
}

function missingGoogleEnv() {
  return ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN", "GOOGLE_CALENDAR_ID"].filter(
    (name) => !process.env[name]
  );
}

function requireGoogleEnv() {
  const missing = missingGoogleEnv();
  if (missing.length) {
    throw new PublicBookingError(
      503,
      "booking_unconfigured",
      "نظام الحجز يحتاج تفعيل الربط مع Google Calendar قبل استقبال المواعيد.",
      { missingEnv: missing }
    );
  }
}

async function getAccessToken() {
  requireGoogleEnv();

  const body = new URLSearchParams({
    client_id: process.env.GOOGLE_CLIENT_ID,
    client_secret: process.env.GOOGLE_CLIENT_SECRET,
    refresh_token: process.env.GOOGLE_REFRESH_TOKEN,
    grant_type: "refresh_token",
  });

  const response = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok || !data.access_token) {
    throw new PublicBookingError(
      503,
      "calendar_auth_failed",
      "تعذر الاتصال بتقويم المواعيد حالياً. يمكنك المحاولة لاحقاً أو التواصل عبر واتساب."
    );
  }

  return data.access_token;
}

async function googleCalendarJson(accessToken, path, options = {}) {
  const response = await fetch(`https://www.googleapis.com/calendar/v3/${path}`, {
    method: options.method || "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error?.message || "Google Calendar request failed");
    error.status = response.status;
    error.google = data;
    throw error;
  }

  return data;
}

async function freeBusy(accessToken, timeMin, timeMax, config) {
  const calendarId = process.env.GOOGLE_CALENDAR_ID;
  const data = await googleCalendarJson(accessToken, "freeBusy", {
    method: "POST",
    body: {
      timeMin,
      timeMax,
      timeZone: config.timezone,
      items: [{ id: calendarId }],
    },
  });

  return data.calendars?.[calendarId]?.busy || [];
}

async function availableSlots(daysAhead, limit = 60) {
  const config = bookingConfigFromEnv();
  const candidates = generateCandidateSlots(daysAhead, config);
  if (!candidates.length) return { config, slots: [] };

  const accessToken = await getAccessToken();
  const busy = await freeBusy(accessToken, candidates[0].start, candidates[candidates.length - 1].end, config);

  const slots = candidates.filter((slot) => !busy.some((busyItem) => overlaps(slot, busyItem))).slice(0, limit);
  return { config, slots };
}

async function nearestSlots(daysAhead, excludedSlot) {
  const result = await availableSlots(daysAhead, 8);
  return result.slots.filter((slot) => slot.slot !== excludedSlot).slice(0, 6);
}

function deterministicEventId(calendarId, slot) {
  const hash = crypto.createHash("sha256").update(`${calendarId}:${slot}`).digest("hex").slice(0, 48);
  return `cal${hash}`;
}

function normalizeText(value, maxLength) {
  return String(value || "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, maxLength);
}

function validateEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i.test(String(value || "").trim());
}

function validateBookingInput(payload) {
  const data = {
    slot: normalizeText(payload.slot, 64),
    fullName: normalizeText(payload.fullName, 100),
    email: normalizeText(payload.email, 160).toLowerCase(),
    mobile: normalizeText(payload.mobile, 40),
    projectStatus: normalizeText(payload.projectStatus, 60),
    platform: normalizeText(payload.platform, 60),
    requirement: normalizeText(payload.requirement, 160),
    notes: normalizeText(payload.notes, 600),
    website: normalizeText(payload.website, 120),
  };

  if (data.website) {
    throw new PublicBookingError(400, "invalid_request", "تعذر قبول الطلب.");
  }

  if (!parseSlot(data.slot)) {
    throw new PublicBookingError(422, "invalid_slot", "اختر موعداً صحيحاً من المواعيد المتاحة.");
  }

  if (data.fullName.length < 2) {
    throw new PublicBookingError(422, "invalid_name", "اكتب الاسم الكامل.");
  }

  if (!validateEmail(data.email)) {
    throw new PublicBookingError(422, "invalid_email", "اكتب بريد إلكتروني صحيح لاستلام دعوة Google Calendar.");
  }

  if (data.mobile.length < 7 || !/^[+\d\s()-]+$/.test(data.mobile)) {
    throw new PublicBookingError(422, "invalid_mobile", "اكتب رقم جوال صحيح.");
  }

  if (!data.projectStatus || !data.platform || !data.requirement) {
    throw new PublicBookingError(422, "missing_details", "أكمل تفاصيل المشروع الأساسية.");
  }

  return data;
}

function eventDescription(input) {
  const lines = [
    "طلب استشارة من موقع إزهلها.",
    "",
    `الحالة: ${input.projectStatus}`,
    `المنصة: ${input.platform}`,
    `الاحتياج: ${input.requirement}`,
    `الجوال / واتساب: ${input.mobile}`,
  ];

  if (input.notes) {
    lines.push("", "ملاحظات:", input.notes);
  }

  return lines.join("\n");
}

function buildCalendarEvent(input, slot, eventId, config) {
  return {
    id: eventId,
    summary: `استشارة إزهلها - ${input.fullName}`,
    description: eventDescription(input),
    start: {
      dateTime: slot.start,
      timeZone: config.timezone,
    },
    end: {
      dateTime: slot.end,
      timeZone: config.timezone,
    },
    attendees: [
      {
        email: input.email,
        displayName: input.fullName,
      },
    ],
    guestsCanInviteOthers: false,
    guestsCanModify: false,
    guestsCanSeeOtherGuests: false,
    conferenceData: {
      createRequest: {
        requestId: eventId,
        conferenceSolutionKey: { type: "hangoutsMeet" },
      },
    },
    extendedProperties: {
      private: {
        source: "ezhalhe-sa.com",
        slot: input.slot,
        projectStatus: input.projectStatus,
        platform: input.platform,
      },
    },
  };
}

function extractMeetUrl(event) {
  if (event.hangoutLink) return event.hangoutLink;

  const entryPoints = event.conferenceData?.entryPoints || [];
  const video = entryPoints.find((entry) => entry.entryPointType === "video" && entry.uri);
  return video?.uri || null;
}

function conferenceCreateStatus(event) {
  return event.conferenceData?.createRequest?.status?.statusCode || "";
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function resolveMeetUrl(accessToken, eventId, initialEvent) {
  const initialUrl = extractMeetUrl(initialEvent);
  if (initialUrl) return initialUrl;

  let status = conferenceCreateStatus(initialEvent);
  if (status && !["pending", "success"].includes(status)) return null;

  const calendarId = encodeURIComponent(process.env.GOOGLE_CALENDAR_ID);
  const encodedEventId = encodeURIComponent(eventId);
  const delays = [700, 1200, 1800];

  for (const delay of delays) {
    await wait(delay);
    const event = await googleCalendarJson(
      accessToken,
      `calendars/${calendarId}/events/${encodedEventId}?conferenceDataVersion=1`
    );
    const url = extractMeetUrl(event);
    if (url) return url;
    status = conferenceCreateStatus(event);
    if (status && !["pending", "success"].includes(status)) return null;
  }

  return null;
}

async function ensureSlotAvailable(accessToken, requestedSlot, config) {
  const candidates = generateCandidateSlots(config.maxDaysAhead, config);
  const slot = candidates.find((candidate) => candidate.slot === requestedSlot);

  if (!slot) {
    throw new PublicBookingError(409, "slot_unavailable", "هذا الموعد غير متاح حالياً.", {
      alternatives: await nearestSlots(config.maxDaysAhead, requestedSlot),
    });
  }

  const busy = await freeBusy(accessToken, slot.start, slot.end, config);
  if (busy.some((busyItem) => overlaps(slot, busyItem))) {
    throw new PublicBookingError(409, "slot_taken", "هذا الموعد تم حجزه للتو. اختر أحد المواعيد التالية.", {
      alternatives: await nearestSlots(config.maxDaysAhead, requestedSlot),
    });
  }

  return slot;
}

async function handleAvailability(req, res) {
  method(req, ["GET"]);
  cleanRateBuckets();

  const ip = clientAddress(req);
  if (rateLimitExceeded(availabilityBuckets, ip, 90)) {
    throw new PublicBookingError(429, "too_many_requests", "طلبات كثيرة خلال وقت قصير. حاول بعد دقائق.");
  }

  const url = new URL(req.url, "https://www.ezhalhe-sa.com");
  const days = Number.parseInt(url.searchParams.get("days") || "", 10);
  const result = await availableSlots(Number.isInteger(days) ? days : 14, 80);

  sendJson(res, 200, {
    ok: true,
    timezone: result.config.timezone,
    durationMinutes: result.config.durationMinutes,
    slots: result.slots,
  });
}

async function handleBooking(req, res) {
  method(req, ["POST"]);
  cleanRateBuckets();

  if (!isSameOrigin(req)) {
    throw new PublicBookingError(403, "forbidden", "تعذر قبول الطلب من هذا المصدر.");
  }

  const ip = clientAddress(req);
  if (rateLimitExceeded(bookingBuckets, ip, 12)) {
    throw new PublicBookingError(429, "too_many_requests", "طلبات كثيرة خلال وقت قصير. حاول بعد دقائق.");
  }

  const input = validateBookingInput(await readJsonBody(req));
  const config = bookingConfigFromEnv();
  const accessToken = await getAccessToken();
  const slot = await ensureSlotAvailable(accessToken, input.slot, config);
  const eventId = deterministicEventId(process.env.GOOGLE_CALENDAR_ID, input.slot);
  const calendarId = encodeURIComponent(process.env.GOOGLE_CALENDAR_ID);

  let event;
  try {
    event = await googleCalendarJson(
      accessToken,
      `calendars/${calendarId}/events?sendUpdates=all&conferenceDataVersion=1`,
      {
        method: "POST",
        body: buildCalendarEvent(input, slot, eventId, config),
      }
    );
  } catch (error) {
    if (error.status === 409) {
      throw new PublicBookingError(409, "slot_taken", "هذا الموعد تم حجزه للتو. اختر أحد المواعيد التالية.", {
        alternatives: await nearestSlots(config.maxDaysAhead, input.slot),
      });
    }
    throw error;
  }

  const meetUrl = await resolveMeetUrl(accessToken, eventId, event);

  sendJson(res, 200, {
    ok: true,
    message: meetUrl
      ? "تم تأكيد موعدك وإرسال دعوة Google Calendar مع رابط Google Meet."
      : "تم تأكيد موعدك، وسيصل رابط Google Meet ضمن دعوة التقويم.",
    appointment: {
      slot: slot.slot,
      dateLabel: slot.dateLabel,
      timeLabel: slot.timeLabel,
      durationMinutes: config.durationMinutes,
      timezone: config.timezone,
      meetUrl,
    },
  });
}

module.exports = {
  PublicBookingError,
  handleAvailability,
  handleBooking,
  handleError,
  sendJson,
};

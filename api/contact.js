"use strict";

const WINDOW_MS = 10 * 60 * 1000;
const MAX_REQUESTS_PER_WINDOW = 5;
const MAX_NAME_LENGTH = 80;
const MAX_EMAIL_LENGTH = 254;
const MAX_MESSAGE_LENGTH = 2000;
const MIN_FORM_COMPLETION_MS = 1500;
const requestWindows = new Map();

function sendJson(response, status, body) {
  response.statusCode = status;
  response.setHeader("Content-Type", "application/json; charset=utf-8");
  response.setHeader("Cache-Control", "no-store");
  response.end(JSON.stringify(body));
}

function requestHost(request) {
  const forwarded = request.headers["x-forwarded-host"];
  return String(Array.isArray(forwarded) ? forwarded[0] : forwarded || request.headers.host || "")
    .split(",", 1)[0]
    .trim()
    .toLowerCase();
}

function isSameOrigin(request) {
  const origin = request.headers.origin;
  if (!origin) return true;

  try {
    return new URL(origin).host.toLowerCase() === requestHost(request);
  } catch {
    return false;
  }
}

function clientAddress(request) {
  const forwarded = request.headers["x-forwarded-for"];
  return String(Array.isArray(forwarded) ? forwarded[0] : forwarded || request.socket?.remoteAddress || "unknown")
    .split(",", 1)[0]
    .trim();
}

function rateLimitExceeded(key, now = Date.now()) {
  const recent = (requestWindows.get(key) || []).filter((timestamp) => now - timestamp < WINDOW_MS);
  recent.push(now);
  requestWindows.set(key, recent);

  if (requestWindows.size > 500) {
    for (const [storedKey, timestamps] of requestWindows.entries()) {
      if (!timestamps.some((timestamp) => now - timestamp < WINDOW_MS)) {
        requestWindows.delete(storedKey);
      }
    }
  }

  return recent.length > MAX_REQUESTS_PER_WINDOW;
}

function normalize(value) {
  return typeof value === "string" ? value.trim() : "";
}

function validEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/u.test(email);
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

async function readJsonBody(request) {
  if (request.body && typeof request.body === "object") return request.body;
  if (typeof request.body === "string") return JSON.parse(request.body);

  let body = "";
  for await (const chunk of request) {
    body += chunk;
    if (body.length > 12_000) throw new Error("payload_too_large");
  }
  return JSON.parse(body || "{}");
}

async function sendTelegramMessage(token, chatId, text) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: chatId, text, parse_mode: "HTML" }),
      signal: controller.signal,
    });
    const payload = await response.json().catch(() => null);
    return response.ok && payload?.ok === true;
  } finally {
    clearTimeout(timeout);
  }
}

module.exports = async function contactHandler(request, response) {
  if (request.method !== "POST") {
    response.setHeader("Allow", "POST");
    return sendJson(response, 405, { ok: false, error: "method_not_allowed" });
  }
  if (!isSameOrigin(request)) {
    return sendJson(response, 403, { ok: false, error: "origin_not_allowed" });
  }
  if (rateLimitExceeded(clientAddress(request))) {
    return sendJson(response, 429, { ok: false, error: "rate_limited" });
  }

  let body;
  try {
    body = await readJsonBody(request);
  } catch {
    return sendJson(response, 400, { ok: false, error: "invalid_request" });
  }

  const name = normalize(body.name);
  const email = normalize(body.email);
  const message = normalize(body.message);
  const website = normalize(body.website);
  const startedAt = Number(body.startedAt);
  const completedTooFast = !Number.isFinite(startedAt) || Date.now() - startedAt < MIN_FORM_COMPLETION_MS;

  if (website || completedTooFast) {
    return sendJson(response, 200, { ok: true });
  }
  if (
    name.length < 2 ||
    name.length > MAX_NAME_LENGTH ||
    email.length > MAX_EMAIL_LENGTH ||
    !validEmail(email) ||
    message.length < 10 ||
    message.length > MAX_MESSAGE_LENGTH
  ) {
    return sendJson(response, 422, { ok: false, error: "validation_failed" });
  }

  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) {
    return sendJson(response, 503, { ok: false, error: "service_unavailable" });
  }

  const text = [
    "<b>رسالة جديدة — إزهلها</b>",
    `<b>الاسم:</b> ${escapeHtml(name)}`,
    `<b>البريد:</b> ${escapeHtml(email)}`,
    `<b>الرسالة:</b> ${escapeHtml(message)}`,
  ].join("\n");

  try {
    const delivered = await sendTelegramMessage(token, chatId, text);
    if (!delivered) {
      return sendJson(response, 502, { ok: false, error: "delivery_failed" });
    }
    return sendJson(response, 200, { ok: true });
  } catch {
    return sendJson(response, 502, { ok: false, error: "delivery_failed" });
  }
};

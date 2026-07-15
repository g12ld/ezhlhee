"use strict";

const handler = require("../api/contact.js");

function responseMock() {
  return {
    statusCode: 200,
    headers: {},
    body: "",
    setHeader(name, value) {
      this.headers[name.toLowerCase()] = value;
    },
    end(value = "") {
      this.body = value;
    },
  };
}

function requestMock({ method = "POST", body = {}, host = "preview.example", origin, ip }) {
  const headers = { host, "x-forwarded-for": ip || `192.0.2.${Math.floor(Math.random() * 200) + 1}` };
  if (origin) headers.origin = origin;
  return { method, body, headers, socket: {} };
}

async function execute(request) {
  const response = responseMock();
  await handler(request, response);
  return { status: response.statusCode, payload: JSON.parse(response.body) };
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function main() {
  const originalFetch = global.fetch;
  const originalToken = process.env.TELEGRAM_BOT_TOKEN;
  const originalChat = process.env.TELEGRAM_CHAT_ID;
  const startedAt = Date.now() - 5000;
  const validBody = {
    name: "عميل تجريبي",
    email: "test@example.com",
    message: "هذه رسالة اختبار آمنة للنموذج.",
    website: "",
    startedAt,
  };

  try {
    delete process.env.TELEGRAM_BOT_TOKEN;
    delete process.env.TELEGRAM_CHAT_ID;

    const method = await execute(requestMock({ method: "GET", ip: "192.0.2.1" }));
    assert(method.status === 405, "GET must return 405");

    const origin = await execute(requestMock({
      body: validBody,
      origin: "https://attacker.example",
      ip: "192.0.2.2",
    }));
    assert(origin.status === 403, "Cross-origin request must return 403");

    const bot = await execute(requestMock({
      body: { ...validBody, website: "spam.example" },
      origin: "https://preview.example",
      ip: "192.0.2.3",
    }));
    assert(bot.status === 200 && bot.payload.ok === true, "Honeypot must fail closed silently");

    const invalid = await execute(requestMock({
      body: { ...validBody, message: "قصير" },
      origin: "https://preview.example",
      ip: "192.0.2.4",
    }));
    assert(invalid.status === 422, "Invalid payload must return 422");

    const unconfigured = await execute(requestMock({
      body: validBody,
      origin: "https://preview.example",
      ip: "192.0.2.5",
    }));
    assert(unconfigured.status === 503, "Missing environment configuration must return 503");

    process.env.TELEGRAM_BOT_TOKEN = "test-token";
    process.env.TELEGRAM_CHAT_ID = "test-chat";
    global.fetch = async () => ({ ok: true, json: async () => ({ ok: true }) });
    const success = await execute(requestMock({
      body: validBody,
      origin: "https://preview.example",
      ip: "192.0.2.6",
    }));
    assert(success.status === 200 && success.payload.ok === true, "Valid delivery must return 200");

    global.fetch = async () => ({ ok: true, json: async () => ({ ok: false }) });
    const telegramFailure = await execute(requestMock({
      body: validBody,
      origin: "https://preview.example",
      ip: "192.0.2.7",
    }));
    assert(telegramFailure.status === 502, "Telegram API failure payload must return 502");

    process.stdout.write(JSON.stringify({ tests: 7, passed: 7, failed: 0 }) + "\n");
  } finally {
    global.fetch = originalFetch;
    if (originalToken === undefined) delete process.env.TELEGRAM_BOT_TOKEN;
    else process.env.TELEGRAM_BOT_TOKEN = originalToken;
    if (originalChat === undefined) delete process.env.TELEGRAM_CHAT_ID;
    else process.env.TELEGRAM_CHAT_ID = originalChat;
  }
}

main().catch((error) => {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 1;
});

(function () {
  "use strict";

  const config = window.EZHALHA_CONFIG || {};
  const company = config.company || {};
  const bookingRules = config.booking || {};
  const whatsappNumber = company.whatsappNumber || "966503228029";
  const RIYADH_OFFSET_MINUTES = 180;

  const state = {
    slots: [],
    selectedDate: "",
    selectedSlot: null,
    submitting: false,
  };

  const elements = {
    alert: document.getElementById("booking-alert"),
    loading: document.getElementById("booking-loading"),
    dateList: document.getElementById("booking-date-list"),
    slotList: document.getElementById("booking-slot-list"),
    refresh: document.getElementById("refresh-slots"),
    form: document.getElementById("booking-form"),
    slotInput: document.getElementById("booking-slot-input"),
    selectedSummary: document.getElementById("selected-slot-summary"),
    submit: document.getElementById("booking-submit"),
  };

  function track(eventName, params) {
    if (typeof window.gtag === "function") {
      window.gtag("event", eventName, params || {});
    }
  }

  function setAlert(message, type) {
    if (!elements.alert) return;
    elements.alert.textContent = message || "";
    elements.alert.classList.toggle("is-visible", Boolean(message));
    elements.alert.classList.toggle("is-error", type === "error");
  }

  function setLoading(active, message) {
    if (!elements.loading) return;
    elements.loading.hidden = !active;
    if (message) elements.loading.textContent = message;
  }

  function groupByDate(slots) {
    return slots.reduce((groups, slot) => {
      if (!groups.has(slot.date)) groups.set(slot.date, []);
      groups.get(slot.date).push(slot);
      return groups;
    }, new Map());
  }

  function pad(value) {
    return String(value).padStart(2, "0");
  }

  function parseTime(value, fallback) {
    const raw = String(value || fallback).trim();
    const match = raw.match(/^([01]\d|2[0-3]):([0-5]\d)$/);
    if (!match) return parseTime(fallback, "12:00");
    return Number(match[1]) * 60 + Number(match[2]);
  }

  function addDays(dateString, amount) {
    const [year, month, day] = dateString.split("-").map(Number);
    return new Date(Date.UTC(year, month - 1, day + amount, 12, 0, 0)).toISOString().slice(0, 10);
  }

  function riyadhDateFromMs(ms) {
    return new Date(ms + RIYADH_OFFSET_MINUTES * 60_000).toISOString().slice(0, 10);
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

  function generateSlots() {
    const durationMinutes = Number(bookingRules.durationMinutes) || 30;
    const bufferMinutes = Number(bookingRules.bufferMinutes) || 0;
    const minNoticeHours = Number(bookingRules.minNoticeHours) || 4;
    const maxDaysAhead = Math.min(Number(bookingRules.maxDaysAhead) || 21, 21);
    const startTimeMinutes = parseTime(bookingRules.startTime, "12:00");
    const endTimeMinutes = parseTime(bookingRules.endTime, "22:00");
    const today = riyadhDateFromMs(Date.now());
    const minStart = Date.now() + minNoticeHours * 60 * 60_000;
    const step = durationMinutes + bufferMinutes;
    const slots = [];

    for (let dayOffset = 0; dayOffset <= maxDaysAhead; dayOffset += 1) {
      const date = addDays(today, dayOffset);

      for (let minutes = startTimeMinutes; minutes <= endTimeMinutes; minutes += step) {
        const startMs = localRiyadhToUtcMs(date, minutes);
        if (startMs < minStart) continue;

        slots.push({
          slot: toRiyadhDateTime(date, minutes),
          date,
          dateLabel: formatArabicDate(date),
          timeLabel: formatArabicTime(minutes),
          durationMinutes,
          timezone: bookingRules.timezone || "Asia/Riyadh",
        });
      }
    }

    return slots;
  }

  function renderDates() {
    const grouped = groupByDate(state.slots);
    elements.dateList.innerHTML = "";

    for (const [date, slots] of grouped.entries()) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "booking-date";
      button.textContent = slots[0].dateLabel;
      button.dataset.date = date;
      button.setAttribute("aria-pressed", String(date === state.selectedDate));
      button.classList.toggle("is-active", date === state.selectedDate);
      button.addEventListener("click", () => selectDate(date));
      elements.dateList.append(button);
    }
  }

  function renderSlots() {
    const slots = state.slots.filter((slot) => slot.date === state.selectedDate);
    elements.slotList.innerHTML = "";

    slots.forEach((slot) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "booking-slot";
      button.textContent = slot.timeLabel;
      button.dataset.slot = slot.slot;
      button.setAttribute("aria-pressed", String(state.selectedSlot?.slot === slot.slot));
      button.classList.toggle("is-active", state.selectedSlot?.slot === slot.slot);
      button.addEventListener("click", () => selectSlot(slot));
      elements.slotList.append(button);
    });
  }

  function setStep(step) {
    document.querySelectorAll("[data-step-indicator]").forEach((indicator) => {
      indicator.classList.toggle("is-active", indicator.dataset.stepIndicator === String(step));
    });
  }

  function selectDate(date) {
    state.selectedDate = date;
    renderDates();
    renderSlots();
  }

  function selectSlot(slot) {
    state.selectedSlot = slot;
    elements.slotInput.value = slot.slot;
    elements.selectedSummary.textContent = `${slot.dateLabel}، ${slot.timeLabel} - مدة الاستشارة ${slot.durationMinutes || 30} دقيقة.`;
    elements.submit.disabled = false;
    elements.form.classList.add("is-ready");
    setStep(2);
    renderSlots();
    setAlert("");
    track("booking_slot_select", { timezone: slot.timezone || "Asia/Riyadh" });
    elements.form.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderEmptyState(message) {
    elements.dateList.innerHTML = "";
    elements.slotList.innerHTML = "";
    setAlert(message, "error");
  }

  function renderAvailability(slots) {
    state.slots = slots;
    state.selectedSlot = null;
    elements.slotInput.value = "";
    elements.submit.disabled = true;
    elements.form.classList.remove("is-ready");

    if (!slots.length) {
      renderEmptyState("لا توجد مواعيد متاحة حالياً. يمكنك التواصل عبر واتساب وسنرتب موعداً مناسباً.");
      return;
    }

    state.selectedDate = slots[0].date;
    renderDates();
    renderSlots();
    setAlert("المواعيد متاحة يومياً من 12 ظهراً إلى 10 مساءً بتوقيت السعودية.");
  }

  function loadAvailability() {
    setLoading(true, "جاري تجهيز المواعيد المتاحة...");
    setAlert("");

    renderAvailability(generateSlots());
    setLoading(false);
  }

  function validateForm() {
    if (!state.selectedSlot) {
      setAlert("اختر موعداً قبل إرسال الطلب.", "error");
      return false;
    }

    if (!elements.form.checkValidity()) {
      elements.form.reportValidity();
      setAlert("فضلاً أكمل البيانات المطلوبة.", "error");
      return false;
    }

    return true;
  }

  function formPayload() {
    const formData = new FormData(elements.form);
    return {
      slot: state.selectedSlot.slot,
      fullName: String(formData.get("fullName") || "").trim(),
      email: String(formData.get("email") || "").trim(),
      mobile: String(formData.get("mobile") || "").trim(),
      projectStatus: String(formData.get("projectStatus") || "").trim(),
      platform: String(formData.get("platform") || "").trim(),
      requirement: String(formData.get("requirement") || "").trim(),
      notes: String(formData.get("notes") || "").trim(),
      website: String(formData.get("website") || "").trim(),
    };
  }

  function bookingWhatsAppUrl(payload) {
    const slot = state.selectedSlot;
    const lines = [
      "مرحباً، أرغب بحجز استشارة مع إزهلها.",
      `الموعد: ${slot.dateLabel} - ${slot.timeLabel}`,
      `المدة: ${slot.durationMinutes || 30} دقيقة`,
      `الاسم: ${payload.fullName}`,
      `الجوال: ${payload.mobile}`,
      payload.email ? `البريد: ${payload.email}` : "",
      `حالة المشروع: ${payload.projectStatus}`,
      `المنصة: ${payload.platform}`,
      `الاحتياج: ${payload.requirement}`,
      payload.notes ? `ملاحظات: ${payload.notes}` : "",
    ].filter(Boolean);

    return `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(lines.join("\n"))}`;
  }

  function submitBooking(event) {
    event.preventDefault();
    if (state.submitting || !validateForm()) return;

    state.submitting = true;
    elements.submit.disabled = true;
    elements.submit.textContent = "جاري فتح واتساب...";
    setAlert("");
    track("booking_whatsapp_redirect");
    window.location.href = bookingWhatsAppUrl(formPayload());
  }

  function wireWhatsAppTracking() {
    document.querySelectorAll("[data-whatsapp-fallback]").forEach((link) => {
      link.href = link.href.replace("966503228029", whatsappNumber);
      link.addEventListener("click", () => track("whatsapp_click", { placement: "booking" }));
    });
  }

  function init() {
    if (!elements.form || !elements.dateList || !elements.slotList) return;
    track("booking_view");
    elements.refresh?.addEventListener("click", loadAvailability);
    elements.form.addEventListener("submit", submitBooking);
    wireWhatsAppTracking();
    loadAvailability();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();

/* Rozmary Digital — menu, formulieren en klikmeting. Alles werkt ook zonder JS. */
(function () {
  "use strict";
  var body = document.body;

  // Mobiel menu
  var toggle = document.querySelector(".menu-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
  // Submenu Diensten (klik/touch)
  document.querySelectorAll(".sub-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var li = btn.closest(".has-sub");
      var open = li.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      body.classList.remove("nav-open");
      if (toggle) toggle.setAttribute("aria-expanded", "false");
      document.querySelectorAll(".has-sub.open").forEach(function (li) { li.classList.remove("open"); });
    }
  });

  // Klikmeting (klaar voor GA4/GTM; er wordt niets verstuurd zolang er geen tag is)
  window.dataLayer = window.dataLayer || [];
  document.addEventListener("click", function (e) {
    var a = e.target.closest("[data-evt]");
    if (a) window.dataLayer.push({ event: a.getAttribute("data-evt"), page: location.pathname });
  });

  // Jaartal
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  // Formulieren
  document.querySelectorAll("form.lead-form").forEach(function (form) {
    var ts = form.querySelector('input[name="ts"]');
    if (ts) ts.value = String(Date.now());

    // Dienst voorselecteren via ?dienst=… (knoppen op de dienstpagina's)
    try {
      var want = new URLSearchParams(location.search).get("dienst");
      var sel = form.querySelector('select[name="interest"]');
      if (want && sel) {
        Array.prototype.forEach.call(sel.options, function (o) { if (o.value === want) sel.value = want; });
        var pkg = new URLSearchParams(location.search).get("pakket");
        var msg = form.querySelector('textarea[name="message"]');
        if (pkg && msg && !msg.value) msg.value = pkg + ": ";
      }
    } catch (err) { /* geen querystring beschikbaar */ }

    var status = form.querySelector(".form-status");
    var fallback = form.querySelector(".form-fallback");
    var waBtn = form.querySelector("[data-wa-fallback]");

    function waText() {
      var f = new FormData(form);
      var intro = form.getAttribute("data-wa-intro") || "";
      var parts = [intro + (f.get("message") || "").toString().trim()];
      ["name", "company", "city", "website", "interest"].forEach(function (k) {
        var v = (f.get(k) || "").toString().trim();
        if (v) parts.push(k + ": " + v);
      });
      return parts.join("\n");
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var btn = form.querySelector('button[type="submit"]');
      var label = btn ? btn.textContent : "";
      if (btn) { btn.disabled = true; btn.textContent = form.getAttribute("data-sending") || "…"; }
      status.className = "form-status"; status.textContent = "";
      fetch(form.getAttribute("data-endpoint"), {
        method: "POST", body: new FormData(form), headers: { "Accept": "application/json" }
      }).then(function (r) {
        return r.json().catch(function () { return { ok: false }; });
      }).then(function (res) {
        if (res && res.ok) {
          window.dataLayer.push({ event: "generate_lead", form: form.id });
          var thanks = form.getAttribute("data-thanks");
          status.className = "form-status ok"; status.textContent = form.getAttribute("data-ok") || "OK";
          if (thanks) setTimeout(function () { location.href = thanks; }, 600);
        } else { throw new Error("send failed"); }
      }).catch(function () {
        status.className = "form-status err"; status.textContent = form.getAttribute("data-fail") || "";
        if (fallback) fallback.hidden = false;
        if (waBtn) waBtn.href = waBtn.getAttribute("data-base") + "?text=" + encodeURIComponent(waText());
      }).finally(function () {
        if (btn) { btn.disabled = false; btn.textContent = label; }
      });
    });
  });
})();

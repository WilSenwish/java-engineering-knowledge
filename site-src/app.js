(function () {
  var root = document.documentElement;
  var mq = window.matchMedia("(prefers-color-scheme: dark)");
  var KEY = "kb-theme";
  var MODES = ["light", "dark", "system"];

  function readMode() {
    try {
      var saved = localStorage.getItem(KEY);
      if (MODES.indexOf(saved) !== -1) return saved;
    } catch (e) {}
    return root.getAttribute("data-theme-mode") || "system";
  }
  function resolved(mode) {
    if (mode === "dark") return "dark";
    if (mode === "light") return "light";
    return mq.matches ? "dark" : "light";
  }
  function paint() {
    var mode = readMode();
    root.setAttribute("data-theme", resolved(mode));
    root.setAttribute("data-theme-mode", mode);
    var btn = document.getElementById("themeBtn");
    var label = mode === "dark" ? "☾ 深色" : mode === "system" ? "◐ 系统" : "☀ 浅色";
    if (btn) btn.textContent = label;
    var fab = document.querySelector(".theme-toggle");
    if (fab) fab.textContent = label;
  }
  function cycle() {
    var mode = readMode();
    var next = MODES[(MODES.indexOf(mode) + 1) % MODES.length];
    try { localStorage.setItem(KEY, next); } catch (e) {}
    paint();
  }
  var themeBtn = document.getElementById("themeBtn");
  if (themeBtn) themeBtn.addEventListener("click", cycle);
  if (mq.addEventListener) mq.addEventListener("change", function () { if (readMode() === "system") paint(); });

  function fab(cls, text, title, onClick) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = cls;
    b.textContent = text;
    b.setAttribute("aria-label", title);
    b.addEventListener("click", onClick);
    document.body.appendChild(b);
    return b;
  }
  var toTop = fab("back-to-top", "↑", "回到顶部", function () {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
  var toBottom = fab("go-to-bottom", "↓", "去到底部", function () {
    window.scrollTo({ top: document.documentElement.scrollHeight, behavior: "smooth" });
  });
  fab("theme-toggle", "", "切换颜色主题", cycle);
  paint();

  function scrollState() {
    var y = window.scrollY || 0;
    var remain = document.documentElement.scrollHeight - y - window.innerHeight;
    toTop.classList.toggle("visible", y > 360);
    toBottom.classList.toggle("visible", remain > 360);
    var bar = document.getElementById("read-bar");
    if (bar) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      var n = max <= 0 ? 100 : Math.round(Math.min(1, y / max) * 100);
      bar.style.width = n + "%";
    }
  }
  window.addEventListener("scroll", scrollState, { passive: true });
  window.addEventListener("resize", scrollState);
  scrollState();

  var topBtn = document.getElementById("topBtn");
  var botBtn = document.getElementById("botBtn");
  if (topBtn) topBtn.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
  if (botBtn) botBtn.addEventListener("click", function () {
    window.scrollTo({ top: document.documentElement.scrollHeight, behavior: "smooth" });
  });
  var menu = document.getElementById("menuBtn");
  var nav = document.querySelector("nav.toc");
  if (menu && nav) menu.addEventListener("click", function () { nav.classList.toggle("open"); });

  var input = document.getElementById("q");
  var hits = document.getElementById("search-hits");
  var listenBtn = document.getElementById("listenBtn");
  var synth = window.speechSynthesis;
  var queue = [];
  var cursor = 0;
  var playing = false;
  var paused = false;
  var started = false;
  function listenLabel() {
    if (!listenBtn) return;
    if (playing && paused) listenBtn.textContent = "▶ 继续";
    else if (playing) listenBtn.textContent = "⏸ 暂停";
    else listenBtn.textContent = "▶ 听";
    listenBtn.classList.toggle("speaking", playing && !paused);
  }
  function articleText() {
    var article = document.querySelector("article");
    if (!article) return "";
    return (article.innerText || "").replace(/[ \t]+\n/g, "\n").replace(/\n{2,}/g, "\n").trim();
  }
  function splitText(text) {
    var bits = text.split(/(?<=[。！？；\n])/);
    var out = [];
    var buf = "";
    bits.forEach(function (bit) {
      var piece = bit.trim();
      if (!piece) return;
      if ((buf + piece).length > 160 && buf) {
        out.push(buf);
        buf = piece;
      } else buf = (buf ? buf : "") + piece;
    });
    if (buf) out.push(buf);
    return out;
  }
  function pickVoice() {
    var list = synth ? synth.getVoices() : [];
    var i;
    for (i = 0; i < list.length; i++) {
      if (/^zh(-|_)?(CN|Hans)/i.test(list[i].lang)) return list[i];
    }
    for (i = 0; i < list.length; i++) {
      if (/^zh/i.test(list[i].lang)) return list[i];
    }
    return null;
  }
  function speakNext() {
    if (!playing || !synth || cursor >= queue.length) {
      playing = false;
      paused = false;
      listenLabel();
      return;
    }
    var utter = new SpeechSynthesisUtterance(queue[cursor]);
    utter.lang = "zh-CN";
    utter.rate = 1;
    var chosen = pickVoice();
    if (chosen) utter.voice = chosen;
    utter.onend = function () {
      if (!playing) return;
      cursor += 1;
      speakNext();
    };
    utter.onerror = function (ev) {
      if (ev && ev.error === "interrupted") return;
      playing = false;
      paused = false;
      listenLabel();
    };
    synth.speak(utter);
  }
  function startListen() {
    if (!synth) return;
    synth.cancel();
    queue = splitText(articleText());
    cursor = 0;
    if (!queue.length) return;
    playing = true;
    paused = false;
    try { localStorage.setItem("kb-listen", "on"); } catch (e) {}
    speakNext();
    listenLabel();
  }
  function toggleListen() {
    if (!synth) return;
    if (playing && !paused) {
      synth.pause();
      paused = true;
      try { localStorage.setItem("kb-listen", "off"); } catch (e) {}
    } else if (playing && paused) {
      synth.resume();
      paused = false;
      try { localStorage.setItem("kb-listen", "on"); } catch (e) {}
    } else startListen();
    listenLabel();
  }
  if (listenBtn) listenBtn.addEventListener("click", toggleListen);
  window.addEventListener("pagehide", function () { if (synth) synth.cancel(); });
  function wantAuto() {
    try { return (localStorage.getItem("kb-listen") || "on") !== "off"; } catch (e) { return true; }
  }
  function autoListen() {
    if (started || !synth || !wantAuto()) { listenLabel(); return; }
    if (!synth.getVoices().length) return;
    started = true;
    startListen();
  }
  if (synth) {
    autoListen();
    synth.addEventListener("voiceschanged", autoListen);
    setTimeout(function () {
      if (started || !wantAuto()) return;
      started = true;
      startListen();
    }, 700);
  }
  listenLabel();

  if (!input || !hits || !window.SITE_INDEX) return;
  input.addEventListener("input", function () {
    var q = input.value.trim().toLowerCase();
    if (!q) { hits.style.display = "none"; hits.innerHTML = ""; return; }
    var found = window.SITE_INDEX.filter(function (p) {
      return (p.title + " " + p.text).toLowerCase().indexOf(q) >= 0;
    }).slice(0, 12);
    var base = document.body.getAttribute("data-root") || "";
    hits.innerHTML = found.map(function (p) {
      return '<a href="' + base + p.href + '"><strong>' + p.title + '</strong><br><small>' + p.text.slice(0, 90) + "</small></a>";
    }).join("") || "<div style='padding:8px 12px;color:var(--muted)'>没有匹配</div>";
    hits.style.display = "block";
  });
})();

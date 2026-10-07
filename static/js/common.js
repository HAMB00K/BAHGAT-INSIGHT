/* Shared front-end utilities: theme, formatting, chart defaults. */

// ---------------- theme ----------------
(function () {
  var btn = document.getElementById("themeToggle");
  if (btn) {
    btn.addEventListener("click", function () {
      var cur = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      localStorage.setItem("bip-theme", cur);
      location.reload(); // charts re-read CSS tokens on init
    });
  }
})();

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// fixed categorical order - never cycled, never re-assigned on filter
function palette(n) {
  var slots = ["--s1", "--s2", "--s3", "--s4", "--s5", "--s6", "--s7", "--s8"];
  return slots.slice(0, n).map(cssVar);
}

var CURRENCY = document.body.dataset.currency || "AED";

// ---------------- formatters ----------------
function fmtMoney(v) {
  if (v === null || v === undefined) return "–";
  var abs = Math.abs(v);
  if (abs >= 1e9) return CURRENCY + " " + (v / 1e9).toFixed(2) + "B";
  if (abs >= 1e6) return CURRENCY + " " + (v / 1e6).toFixed(2) + "M";
  if (abs >= 1e3) return CURRENCY + " " + (v / 1e3).toFixed(1) + "K";
  return CURRENCY + " " + Number(v).toFixed(0);
}
function fmtInt(v) {
  if (v === null || v === undefined) return "–";
  return Number(v).toLocaleString("en-US");
}
function fmtPct(v, d) {
  if (v === null || v === undefined) return "–";
  return Number(v).toFixed(d === undefined ? 1 : d) + "%";
}

async function getJSON(url) {
  var r = await fetch(url);
  if (!r.ok) throw new Error(url + " -> " + r.status);
  return r.json();
}

// ---------------- Apex defaults ----------------
function apexBase(height) {
  return {
    chart: {
      height: height || 300, fontFamily: "inherit", background: "transparent",
      foreColor: cssVar("--muted"),
      toolbar: { show: false }, zoom: { enabled: false },
      animations: { speed: 450 }
    },
    grid: { borderColor: cssVar("--grid"), strokeDashArray: 0,
            padding: { left: 8, right: 8 } },
    dataLabels: { enabled: false },
    tooltip: { theme: false },
    states: { hover: { filter: { type: "lighten", value: 0.04 } } }
  };
}

function moneyAxis() {
  return { labels: { formatter: function (v) { return fmtMoney(v); } } };
}

function dateAxis() {
  return {
    type: "datetime",
    labels: { datetimeUTC: false, style: { fontSize: "11px" } },
    axisBorder: { color: cssVar("--grid") },
    axisTicks: { color: cssVar("--grid") }
  };
}

// KPI tile renderer -----------------------------------------------------------
function kpiTile(k) {
  var val = k.fmt === "currency" ? fmtMoney(k.value)
          : k.fmt === "pct" ? fmtPct(k.value, k.key === "returns" ? 2 : 1)
          : fmtInt(k.value);
  var d = k.delta;
  var html = '<div class="kpi-label">' + k.label + "</div>" +
             '<div class="kpi-value">' + val + "</div>";
  if (d !== null && d !== undefined) {
    var goodDir = k.invert ? d < 0 : d > 0;
    var cls = goodDir ? "up" : "down";
    var arrow = d >= 0 ? "trending-up" : "trending-down";
    var suffix = k.delta_pts ? " pts" : "%";
    html += '<span class="kpi-delta ' + cls + '"><i data-lucide="' + arrow + '"></i>' +
            (d > 0 ? "+" : "") + d + suffix +
            '<span class="vs">vs prev. period</span></span>';
  }
  return '<div class="card">' + html + "</div>";
}

function severityBadge(sev) {
  var map = {
    "Critical": ["b-critical", "octagon-alert"],
    "High": ["b-high", "triangle-alert"],
    "Medium": ["b-medium", "circle-alert"],
    "Low": ["b-low", "info"]
  };
  var m = map[sev] || map["Low"];
  return '<span class="badge ' + m[0] + '"><i data-lucide="' + m[1] + '"></i>' + sev + "</span>";
}

/* Anomaly Detection page */
(function () {
  var days = 540, severity = "";
  var charts = [];
  function destroyCharts() { charts.forEach(function (c) { c.destroy(); }); charts = []; }

  document.querySelectorAll("#daysSeg button").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll("#daysSeg button").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active"); days = +b.dataset.days; loadChart();
    });
  });
  document.getElementById("sevSel").addEventListener("change", function (e) {
    severity = e.target.value; loadTable();
  });

  async function loadChart() {
    destroyCharts();
    var data = await getJSON("/api/anomaly_series?days=" + days);

    // one marker per anomalous day (worst severity wins)
    var rank = { Critical: 4, High: 3, Medium: 2, Low: 1 };
    var byDay = {};
    data.anomalies.forEach(function (a) {
      if (!byDay[a.date_key] || rank[a.severity] > rank[byDay[a.date_key].severity]) byDay[a.date_key] = a;
    });
    var marks = Object.values(byDay);

    var c = new ApexCharts(document.querySelector("#chartAnomaly"), Object.assign(apexBase(360), {
      chart: { height: 360, fontFamily: "inherit", background: "transparent",
               toolbar: { show: false }, zoom: { enabled: false } },
      series: [
        { name: "Net revenue", type: "line",
          data: data.series.map(function (r) { return [new Date(r.date_key).getTime(), r.net_revenue]; }) },
        { name: "Anomaly", type: "scatter",
          data: marks.map(function (a) { return [new Date(a.date_key).getTime(), a.net_revenue]; }) }
      ],
      colors: [cssVar("--s1"), cssVar("--s8")],
      stroke: { width: [1.6, 0], curve: "straight" },
      markers: { size: [0, 5], strokeWidth: 2, strokeColors: cssVar("--surface"), hover: { size: 7 } },
      xaxis: dateAxis(),
      yaxis: moneyAxis(),
      legend: { position: "top", horizontalAlign: "right" },
      tooltip: {
        shared: false, intersect: false,
        x: { format: "dd MMM yyyy" },
        y: { formatter: function (v) { return fmtMoney(v); } }
      }
    }));
    c.render(); charts.push(c);
  }

  async function loadTable() {
    var alerts = await getJSON("/api/anomalies" + (severity ? "?severity=" + severity : ""));
    var rows = alerts.slice(0, 40).map(function (a) {
      var fmtVal = a.metric === "store_orders"
        ? function (v) { return fmtInt(Math.round(v)) + " orders"; } : fmtMoney;
      var vsExp = (a.expected && a.value !== null)
        ? "<div class='sub'>" + fmtVal(a.value) + " vs " + fmtVal(a.expected) + " expected</div>" : "";
      return "<tr><td>" + a.date_key + "<div class='sub'>" + a.store_name + "</div></td>" +
        "<td>" + severityBadge(a.severity) + "</td>" +
        "<td class='sub'>" + a.method + "</td>" +
        "<td>" + a.description + vsExp + "</td></tr>";
    }).join("");
    document.getElementById("alertTable").innerHTML =
      "<thead><tr><th>Date / scope</th><th>Severity</th><th>Detector</th><th>Diagnosis</th></tr></thead><tbody>" +
      (rows || "<tr><td colspan=4 class='empty'>No alerts for this filter</td></tr>") + "</tbody>";
    lucide.createIcons();
  }

  async function loadValidation() {
    var val = await getJSON("/api/anomaly_validation");
    var kpiHtml =
      '<div class="card"><div class="kpi-label">Injected incidents (ground truth)</div>' +
      '<div class="kpi-value">' + val.length + "</div>" +
      '<span class="card-note">simulated outages, floods, pricing bugs, fraud…</span></div>';
    var detected = val.filter(function (v) { return v.detected; }).length;
    kpiHtml +=
      '<div class="card"><div class="kpi-label">Detected by the ML layer</div>' +
      '<div class="kpi-value">' + detected + " / " + val.length + "</div>" +
      '<span class="card-note">event-level recall of the two detectors combined</span></div>';

    // /api/anomalies is capped at 300 rows for the table - count over the full history instead
    var all = await getJSON("/api/anomaly_series?days=1200");
    kpiHtml +=
      '<div class="card"><div class="kpi-label">Total alerts raised</div>' +
      '<div class="kpi-value">' + fmtInt(all.anomalies.length) + "</div>" +
      '<span class="card-note">across ' + fmtInt(all.series.length) + ' days of history</span></div>';
    document.getElementById("anKpis").innerHTML = kpiHtml;

    document.getElementById("valTable").innerHTML =
      "<thead><tr><th>Injected incident</th><th>Window</th><th>Status</th></tr></thead><tbody>" +
      val.map(function (v) {
        return "<tr><td>" + v.label + "<div class='sub'>stores: " + v.stores + "</div></td>" +
          "<td class='sub'>" + v.start + (v.end !== v.start ? " → " + v.end : "") + "</td>" +
          "<td>" + (v.detected
            ? '<span class="badge b-good"><i data-lucide="check"></i>Detected</span>'
            : '<span class="badge b-critical"><i data-lucide="x"></i>Missed</span>') + "</td></tr>";
      }).join("") + "</tbody>";
    document.getElementById("recallNote").textContent =
      "Because the dataset is synthetic, the incidents are known in advance - this lets us measure " +
      "the detector objectively instead of eyeballing charts.";
    lucide.createIcons();
  }

  loadChart(); loadTable(); loadValidation();
})();

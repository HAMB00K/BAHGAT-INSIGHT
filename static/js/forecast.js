/* Forecasting page */
(function () {
  var charts = [];
  function destroyCharts() { charts.forEach(function (c) { c.destroy(); }); charts = []; }

  async function initScopes() {
    var metrics = await getJSON("/api/forecast_metrics");
    var scopes = [];
    metrics.forEach(function (m) {
      if (m.scope !== "company" && scopes.indexOf(m.scope) === -1) scopes.push(m.scope);
    });
    var sel = document.getElementById("scopeSel");
    scopes.sort().forEach(function (s) {
      var o = document.createElement("option");
      o.value = s; o.textContent = s;
      sel.appendChild(o);
    });
    sel.addEventListener("change", function () { load(sel.value); });
    return metrics;
  }

  async function load(scope) {
    destroyCharts();
    var [rows, metrics] = await Promise.all([
      getJSON("/api/forecast?scope=" + encodeURIComponent(scope)),
      getJSON("/api/forecast_metrics")
    ]);

    var hist = rows.filter(function (r) { return r.kind === "history"; });
    var fc = rows.filter(function (r) { return r.kind === "forecast"; });

    var champ = metrics.find(function (m) { return m.scope === "company" && m.is_champion; }) || {};
    document.getElementById("champName").textContent = champ.model || "-";

    // KPI tiles: next-30-day total, horizon total, champion MAPE
    var scoped = metrics.find(function (m) { return m.scope === scope && m.is_champion; }) ||
                 metrics.find(function (m) { return m.scope === scope; }) || {};
    var next30 = fc.slice(0, 30).reduce(function (a, r) { return a + (r.forecast || 0); }, 0);
    var next90 = fc.reduce(function (a, r) { return a + (r.forecast || 0); }, 0);
    document.getElementById("fcKpis").innerHTML =
      '<div class="card"><div class="kpi-label">Projected revenue — next 30 days</div>' +
      '<div class="kpi-value">' + fmtMoney(next30) + "</div>" +
      '<span class="card-note">' + (scope === "company" ? "whole company" : scope) + "</span></div>" +
      '<div class="card"><div class="kpi-label">Projected revenue — 90-day horizon</div>' +
      '<div class="kpi-value">' + fmtMoney(next90) + "</div>" +
      '<span class="card-note">sum of daily point forecasts</span></div>' +
      '<div class="card"><div class="kpi-label">Backtest accuracy (MAPE)</div>' +
      '<div class="kpi-value">' + fmtPct(scoped.mape, 1) + "</div>" +
      '<span class="card-note">' + (scoped.model || "") + " on 60-day holdout</span></div>";

    // main chart: history line + backtest dashed + forecast line + CI band
    var histLine = hist.map(function (r) { return { x: new Date(r.date_key).getTime(), y: r.actual }; });
    var btLine = hist.filter(function (r) { return r.forecast !== null; })
                     .map(function (r) { return { x: new Date(r.date_key).getTime(), y: r.forecast }; });
    var fcLine = fc.map(function (r) { return { x: new Date(r.date_key).getTime(), y: r.forecast }; });
    var band = fc.map(function (r) { return { x: new Date(r.date_key).getTime(), y: [r.lo, r.hi] }; });

    var c = new ApexCharts(document.querySelector("#chartForecast"), Object.assign(apexBase(380), {
      chart: { type: "rangeArea", height: 380, fontFamily: "inherit",
               background: "transparent", toolbar: { show: false }, zoom: { enabled: false },
               animations: { speed: 400 } },
      series: [
        { name: "95% interval", type: "rangeArea", data: band },
        { name: "Actual revenue", type: "line", data: histLine },
        { name: "Backtest fit", type: "line", data: btLine },
        { name: "Forecast", type: "line", data: fcLine }
      ],
      colors: [cssVar("--seq-250"), cssVar("--s1"), cssVar("--s4"), cssVar("--seq-550")],
      stroke: { width: [0, 2, 2, 2.5], curve: "straight", dashArray: [0, 0, 5, 0] },
      fill: { opacity: [0.35, 1, 1, 1] },
      markers: { size: 0, hover: { size: 4 } },
      xaxis: dateAxis(),
      yaxis: moneyAxis(),
      legend: { position: "top", horizontalAlign: "right" },
      tooltip: { shared: true, x: { format: "dd MMM yyyy" },
        y: { formatter: function (v) {
          if (v === null || v === undefined) return "–";
          return Array.isArray(v) ? fmtMoney(v[0]) + " – " + fmtMoney(v[1]) : fmtMoney(v);
        } } }
    }));
    c.render(); charts.push(c);

    // model comparison table (company scope)
    var comp = metrics.filter(function (m) { return m.scope === "company"; });
    document.getElementById("modelTable").innerHTML =
      "<thead><tr><th>Model</th><th class='num'>MAPE</th><th class='num'>RMSE</th><th>Status</th></tr></thead><tbody>" +
      comp.map(function (m) {
        return "<tr><td>" + m.model + "</td>" +
          "<td class='num'>" + fmtPct(m.mape, 2) + "</td>" +
          "<td class='num'>" + fmtMoney(m.rmse) + "</td>" +
          "<td>" + (m.is_champion
            ? '<span class="badge b-good"><i data-lucide="crown"></i>Champion</span>'
            : '<span class="badge"><i data-lucide="flask-conical"></i>Challenger</span>') + "</td></tr>";
      }).join("") + "</tbody>";
    lucide.createIcons();

    // per-category MAPE bars
    var catM = metrics.filter(function (m) { return m.scope !== "company"; })
                      .sort(function (a, b) { return a.mape - b.mape; });
    var c2 = new ApexCharts(document.querySelector("#chartMape"), Object.assign(apexBase(300), {
      chart: { type: "bar", height: 300, fontFamily: "inherit", background: "transparent", toolbar: { show: false } },
      series: [{ name: "MAPE", data: catM.map(function (m) { return m.mape; }) }],
      colors: [cssVar("--s1")],
      plotOptions: { bar: { horizontal: true, borderRadius: 4, borderRadiusApplication: "end", barHeight: "60%" } },
      xaxis: { categories: catM.map(function (m) { return m.scope; }),
               labels: { formatter: function (v) { return v + "%"; } } },
      tooltip: { y: { formatter: function (v) { return fmtPct(v, 1); } } }
    }));
    c2.render(); charts.push(c2);
  }

  initScopes().then(function () { load("company"); });
})();

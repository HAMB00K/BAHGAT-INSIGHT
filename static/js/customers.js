/* Customer Intelligence page */
(function () {
  var charts = [];

  async function load() {
    var [profiles, scatter, ages, risk] = await Promise.all([
      getJSON("/api/segments"),
      getJSON("/api/segment_scatter"),
      getJSON("/api/demographics"),
      getJSON("/api/at_risk")
    ]);

    // segment donut
    var c1 = new ApexCharts(document.querySelector("#chartSegments"), Object.assign(apexBase(300), {
      chart: { type: "donut", height: 300, fontFamily: "inherit", background: "transparent" },
      series: profiles.map(function (p) { return p.customers; }),
      labels: profiles.map(function (p) { return p.segment; }),
      colors: palette(profiles.length),
      stroke: { colors: [cssVar("--surface")], width: 2 },
      legend: { position: "bottom", fontSize: "12px" },
      dataLabels: { enabled: false },
      plotOptions: { pie: { donut: { size: "68%", labels: { show: true,
        total: { show: true, label: "Members", fontSize: "12px",
          formatter: function (w) {
            return fmtInt(w.globals.seriesTotals.reduce(function (a, b) { return a + b; }, 0));
          } } } } } },
      tooltip: { y: { formatter: function (v) { return fmtInt(v) + " customers"; } } }
    }));
    c1.render(); charts.push(c1);

    // profiles table
    document.getElementById("segTable").innerHTML =
      "<thead><tr><th>Segment</th><th class='num'>Customers</th><th class='num'>Avg spend</th>" +
      "<th class='num'>Avg orders</th><th class='num'>Recency (d)</th><th class='num'>Revenue share</th></tr></thead><tbody>" +
      profiles.map(function (p, i) {
        return "<tr><td><span class='legend-row'><span class='swatch' style='background:" +
          palette(profiles.length)[i] + "'></span><b>" + p.segment + "</b></span></td>" +
          "<td class='num'>" + fmtInt(p.customers) + "</td>" +
          "<td class='num'>" + fmtMoney(p.avg_monetary) + "</td>" +
          "<td class='num'>" + p.avg_frequency.toFixed(1) + "</td>" +
          "<td class='num'>" + Math.round(p.avg_recency_days) + "</td>" +
          "<td class='num'>" + fmtPct(p.revenue_share_pct) + "</td></tr>";
      }).join("") + "</tbody>";

    // scatter: frequency vs monetary, single-hue by churn risk (sequential = magnitude)
    var buckets = [
      { name: "Churn risk < 25%", color: cssVar("--seq-100"), test: function (r) { return r.churn_risk < 0.25; } },
      { name: "25 – 50%", color: cssVar("--seq-250"), test: function (r) { return r.churn_risk >= 0.25 && r.churn_risk < 0.5; } },
      { name: "50 – 75%", color: cssVar("--seq-400"), test: function (r) { return r.churn_risk >= 0.5 && r.churn_risk < 0.75; } },
      { name: "≥ 75%", color: cssVar("--seq-700"), test: function (r) { return r.churn_risk >= 0.75; } }
    ];
    var series = buckets.map(function (b) {
      return { name: b.name, data: scatter.filter(b.test).map(function (r) {
        return { x: r.frequency, y: Math.max(r.monetary, 1), seg: r.segment }; }) };
    });
    var c2 = new ApexCharts(document.querySelector("#chartScatter"), Object.assign(apexBase(320), {
      chart: { type: "scatter", height: 320, fontFamily: "inherit", background: "transparent", toolbar: { show: false }, zoom: { enabled: false } },
      series: series,
      colors: buckets.map(function (b) { return b.color; }),
      markers: { size: 4, strokeWidth: 0, hover: { size: 6 } },
      xaxis: { title: { text: "Orders (frequency)", style: { fontSize: "11px" } },
               tickAmount: 8, labels: { formatter: function (v) { return Math.round(v); } } },
      yaxis: { logarithmic: true, title: { text: "Lifetime spend (log)", style: { fontSize: "11px" } },
               labels: { formatter: function (v) { return fmtMoney(v); } } },
      legend: { position: "top", horizontalAlign: "right" },
      tooltip: { custom: function (o) {
        var p = o.w.config.series[o.seriesIndex].data[o.dataPointIndex];
        return '<div style="padding:8px 10px;font-size:12px"><b>' + p.seg + "</b><br>" +
               p.x + " orders · " + fmtMoney(p.y) + "</div>";
      } }
    }));
    c2.render(); charts.push(c2);

    // age bands (stacked by gender)
    var bands = [];
    ages.forEach(function (a) { if (bands.indexOf(a.age_band) === -1) bands.push(a.age_band); });
    bands.sort();
    function sumFor(g) {
      return bands.map(function (b) {
        var hit = ages.find(function (a) { return a.age_band === b && a.gender === g; });
        return hit ? hit.revenue : 0;
      });
    }
    var c3 = new ApexCharts(document.querySelector("#chartAge"), Object.assign(apexBase(320), {
      chart: { type: "bar", height: 320, stacked: true, fontFamily: "inherit", background: "transparent", toolbar: { show: false } },
      series: [{ name: "Female", data: sumFor("F") }, { name: "Male", data: sumFor("M") }],
      colors: [cssVar("--s3"), cssVar("--s1")],
      plotOptions: { bar: { borderRadius: 4, borderRadiusApplication: "end", columnWidth: "55%" } },
      xaxis: { categories: bands },
      yaxis: moneyAxis(),
      legend: { position: "top", horizontalAlign: "right" },
      tooltip: { y: { formatter: function (v) { return fmtMoney(v); } } }
    }));
    c3.render(); charts.push(c3);

    // churn watchlist
    document.getElementById("riskTable").innerHTML =
      "<thead><tr><th>Customer</th><th>Segment</th><th class='num'>Lifetime spend</th>" +
      "<th class='num'>Orders</th><th class='num'>Days inactive</th>" +
      "<th class='num'>Est. annual CLV</th><th style='width:150px'>Churn risk</th></tr></thead><tbody>" +
      risk.map(function (r) {
        var pctv = Math.round(r.churn_risk * 100);
        return "<tr><td><b>" + r.name + "</b><div class='sub'>" + r.city + " · " + r.customer_id + "</div></td>" +
          "<td class='sub'>" + r.segment + "</td>" +
          "<td class='num'>" + fmtMoney(r.monetary) + "</td>" +
          "<td class='num'>" + fmtInt(r.frequency) + "</td>" +
          "<td class='num'>" + fmtInt(r.recency) + "</td>" +
          "<td class='num'>" + fmtMoney(r.clv_annual) + "</td>" +
          "<td><div style='display:flex;align-items:center;gap:8px'><div class='meter warn' style='flex:1'>" +
          "<span style='width:" + pctv + "%'></span></div>" +
          "<span class='sub' style='min-width:34px'>" + pctv + "%</span></div></td></tr>";
      }).join("") + "</tbody>";
  }

  load();
})();

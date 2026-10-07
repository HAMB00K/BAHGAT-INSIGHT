/* Executive Overview page */
(function () {
  var days = 90;

  document.querySelectorAll("#daysSeg button").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll("#daysSeg button").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active");
      days = +b.dataset.days;
      load();
    });
  });

  var charts = [];
  function destroyCharts() {
    charts.forEach(function (c) { c.destroy(); });
    charts = [];
  }

  async function load() {
    destroyCharts();
    var [kpis, trend, cats, stores, alerts] = await Promise.all([
      getJSON("/api/kpis?days=" + days),
      getJSON("/api/revenue_trend?days=" + days + (days > 120 ? "&granularity=week" : "")),
      getJSON("/api/category_breakdown?days=" + days),
      getJSON("/api/store_performance?days=" + days),
      getJSON("/api/anomalies")
    ]);

    // KPI tiles
    document.getElementById("kpiGrid").innerHTML = kpis.kpis.map(kpiTile).join("");
    lucide.createIcons();

    // trend area + MA7
    var base = apexBase(300);
    var series = [{ name: "Net revenue", type: "area",
                    data: trend.labels.map(function (d, i) { return [new Date(d).getTime(), trend.revenue[i]]; }) }];
    if (trend.ma7) {
      series.push({ name: "7-day average", type: "line",
                    data: trend.labels.map(function (d, i) { return [new Date(d).getTime(), trend.ma7[i]]; }) });
    }
    var c1 = new ApexCharts(document.querySelector("#chartTrend"), Object.assign(base, {
      series: series,
      colors: [cssVar("--s1"), cssVar("--s7")],
      stroke: { width: [2, 2], curve: "smooth" },
      fill: { type: ["gradient", "solid"],
              gradient: { opacityFrom: 0.28, opacityTo: 0.02 } },
      xaxis: dateAxis(),
      yaxis: moneyAxis(),
      legend: { show: true, position: "top", horizontalAlign: "right" },
      tooltip: { shared: true, x: { format: "dd MMM yyyy" },
                 y: { formatter: function (v) { return fmtMoney(v); } } }
    }));
    c1.render(); charts.push(c1);

    // category donut
    var c2 = new ApexCharts(document.querySelector("#chartCat"), Object.assign(apexBase(290), {
      chart: { type: "donut", height: 290, fontFamily: "inherit", background: "transparent" },
      series: cats.map(function (c) { return c.rev; }),
      labels: cats.map(function (c) { return c.category; }),
      colors: palette(cats.length),
      stroke: { colors: [cssVar("--surface")], width: 2 },
      legend: { position: "bottom", fontSize: "12px" },
      dataLabels: { enabled: false },
      plotOptions: { pie: { donut: { size: "68%",
        labels: { show: true, total: { show: true, label: "Total", fontSize: "12px",
          formatter: function (w) {
            return fmtMoney(w.globals.seriesTotals.reduce(function (a, b) { return a + b; }, 0));
          } } } } } },
      tooltip: { y: { formatter: function (v) { return fmtMoney(v); } } }
    }));
    c2.render(); charts.push(c2);

    // stores bar
    var top = stores.slice(0, 8);
    var c3 = new ApexCharts(document.querySelector("#chartStores"), Object.assign(apexBase(300), {
      chart: { type: "bar", height: 300, fontFamily: "inherit", background: "transparent", toolbar: { show: false } },
      series: [{ name: "Net revenue", data: top.map(function (s) { return s.rev; }) }],
      colors: [cssVar("--s1")],
      plotOptions: { bar: { horizontal: true, borderRadius: 4, borderRadiusApplication: "end", barHeight: "62%" } },
      xaxis: Object.assign({ categories: top.map(function (s) { return s.store_name; }) }, moneyAxis()),
      yaxis: { labels: { style: { fontSize: "12px" } } },
      tooltip: { y: { formatter: function (v) { return fmtMoney(v); } } }
    }));
    c3.render(); charts.push(c3);

    // recent alerts table
    var rows = alerts.slice(0, 6).map(function (a) {
      return "<tr><td>" + a.date_key + "<div class='sub'>" + a.store_name + "</div></td>" +
             "<td>" + severityBadge(a.severity) + "</td>" +
             "<td class='sub'>" + a.description + "</td></tr>";
    }).join("");
    document.getElementById("alertTable").innerHTML =
      "<thead><tr><th>Date</th><th>Severity</th><th>Description</th></tr></thead><tbody>" +
      (rows || "<tr><td colspan=3 class='empty'>No anomalies detected</td></tr>") + "</tbody>";
    lucide.createIcons();
  }

  load();
})();

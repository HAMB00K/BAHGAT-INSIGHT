/* Sales Analytics page */
(function () {
  var days = 90, store = "", category = "";
  var periodCharts = [];
  function destroyCharts() { periodCharts.forEach(function (c) { c.destroy(); }); periodCharts = []; }

  document.querySelectorAll("#daysSeg button").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll("#daysSeg button").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active"); days = +b.dataset.days; loadPeriod();
    });
  });

  async function initFilters() {
    var meta = await getJSON("/api/meta");
    var storeSel = document.getElementById("storeSel");
    meta.stores.forEach(function (s) {
      var o = document.createElement("option");
      o.value = s.store_id; o.textContent = s.store_name;
      storeSel.appendChild(o);
    });
    var catSel = document.getElementById("catSel");
    meta.categories.forEach(function (c) {
      var o = document.createElement("option");
      o.value = c; o.textContent = c;
      catSel.appendChild(o);
    });
    storeSel.addEventListener("change", function () { store = storeSel.value; loadProducts(); });
    catSel.addEventListener("change", function () { category = catSel.value; loadProducts(); });
  }

  // full-history charts (not affected by the period filter) -------------------
  async function loadHistory() {
    var monthly = await getJSON("/api/monthly_perf");
    var labels = monthly.map(function (m) { return m.month + "-01"; });

    new ApexCharts(document.querySelector("#chartMonthly"), Object.assign(apexBase(300), {
      chart: { type: "bar", height: 300, fontFamily: "inherit", background: "transparent", toolbar: { show: false } },
      series: [{ name: "Net revenue", data: monthly.map(function (m) { return m.rev; }) }],
      colors: [cssVar("--s1")],
      plotOptions: { bar: { borderRadius: 3, borderRadiusApplication: "end", columnWidth: "70%" } },
      xaxis: { categories: labels, type: "datetime", labels: { datetimeUTC: false, format: "MMM yy" } },
      yaxis: moneyAxis(),
      tooltip: { x: { format: "MMM yyyy" }, y: { formatter: function (v) { return fmtMoney(v); } } }
    })).render();

    new ApexCharts(document.querySelector("#chartMarginRate"), Object.assign(apexBase(300), {
      chart: { type: "line", height: 300, fontFamily: "inherit", background: "transparent",
               toolbar: { show: false }, zoom: { enabled: false } },
      series: [{ name: "Gross margin rate",
                 data: monthly.map(function (m, i) {
                   return [new Date(labels[i]).getTime(), m.rev ? +(m.margin / m.rev * 100).toFixed(2) : null];
                 }) }],
      colors: [cssVar("--s2")],
      stroke: { width: 2.5, curve: "straight" },
      markers: { size: 3, hover: { size: 5 } },
      xaxis: dateAxis(),
      yaxis: { labels: { formatter: function (v) { return fmtPct(v, 1); } } },
      tooltip: { x: { format: "MMM yyyy" }, y: { formatter: function (v) { return fmtPct(v, 2); } } }
    })).render();
  }

  // charts driven by the period filter ----------------------------------------
  async function loadPeriod() {
    destroyCharts();
    var [channel, payments, web] = await Promise.all([
      getJSON("/api/channel_split?days=" + Math.max(days, 365)),
      getJSON("/api/payment_methods?days=" + days),
      getJSON("/api/web_summary?days=" + days)
    ]);

    var c1 = new ApexCharts(document.querySelector("#chartChannel"), Object.assign(apexBase(300), {
      chart: { type: "bar", height: 300, stacked: true, fontFamily: "inherit", background: "transparent", toolbar: { show: false } },
      series: [{ name: "In-store", data: channel.instore }, { name: "Online", data: channel.online }],
      colors: [cssVar("--s1"), cssVar("--s3")],
      plotOptions: { bar: { borderRadius: 3, borderRadiusApplication: "end", columnWidth: "60%" } },
      xaxis: { categories: channel.months },
      yaxis: moneyAxis(),
      legend: { position: "top", horizontalAlign: "right" },
      tooltip: { shared: true, intersect: false, y: { formatter: function (v) { return fmtMoney(v); } } }
    }));
    c1.render(); periodCharts.push(c1);

    var c2 = new ApexCharts(document.querySelector("#chartPayment"), Object.assign(apexBase(300), {
      chart: { type: "bar", height: 300, fontFamily: "inherit", background: "transparent", toolbar: { show: false } },
      series: [{ name: "Net revenue", data: payments.map(function (p) { return p.rev; }) }],
      colors: [cssVar("--s1")],
      plotOptions: { bar: { horizontal: true, borderRadius: 4, borderRadiusApplication: "end", barHeight: "60%" } },
      xaxis: Object.assign({ categories: payments.map(function (p) { return p.payment_method; }) }, moneyAxis()),
      tooltip: { y: { formatter: function (v, o) {
        return fmtMoney(v) + " · " + fmtInt(payments[o.dataPointIndex].orders) + " orders";
      } } }
    }));
    c2.render(); periodCharts.push(c2);

    document.getElementById("webKpis").innerHTML =
      '<div><div class="kpi-label">Sessions</div><div class="kpi-value">' + fmtInt(web.sessions) + "</div></div>" +
      '<div><div class="kpi-label">Online orders</div><div class="kpi-value">' + fmtInt(web.orders) + "</div></div>" +
      '<div><div class="kpi-label">Conversion rate</div><div class="kpi-value">' + fmtPct(web.conversion_rate, 2) + "</div></div>" +
      '<div><div class="kpi-label">Bounce rate</div><div class="kpi-value">' + fmtPct(web.bounce_rate, 1) + "</div></div>";

    var c3 = new ApexCharts(document.querySelector("#chartWeb"), Object.assign(apexBase(220), {
      chart: { type: "area", height: 220, fontFamily: "inherit", background: "transparent",
               toolbar: { show: false }, zoom: { enabled: false } },
      series: [{ name: "Sessions",
                 data: web.trend.map(function (r) { return [new Date(r.date).getTime(), r.sessions]; }) }],
      colors: [cssVar("--s1")],
      stroke: { width: 2, curve: "smooth" },
      fill: { type: "gradient", gradient: { opacityFrom: 0.28, opacityTo: 0.02 } },
      xaxis: dateAxis(),
      yaxis: { labels: { formatter: function (v) { return fmtInt(Math.round(v)); } } },
      tooltip: { x: { format: "dd MMM yyyy" }, y: { formatter: function (v) { return fmtInt(v); } } }
    }));
    c3.render(); periodCharts.push(c3);

    loadProducts();
  }

  async function loadProducts() {
    var url = "/api/top_products?days=" + days +
              "&store=" + encodeURIComponent(store) + "&category=" + encodeURIComponent(category);
    var rows = await getJSON(url);
    var storeSel = document.getElementById("storeSel");
    var scope = [store ? storeSel.options[storeSel.selectedIndex].text : null, category || null]
                  .filter(Boolean).join(" · ");
    document.getElementById("topDesc").textContent =
      "By net revenue, last " + days + " days" + (scope ? " — " + scope : "");
    document.getElementById("prodTable").innerHTML =
      "<thead><tr><th>Product</th><th class='num'>Units</th><th class='num'>Net revenue</th>" +
      "<th class='num'>Margin</th></tr></thead><tbody>" +
      (rows.map(function (r) {
        return "<tr><td><b>" + r.product_name + "</b><div class='sub'>" + r.category + " · " + r.brand + "</div></td>" +
          "<td class='num'>" + fmtInt(r.units) + "</td>" +
          "<td class='num'>" + fmtMoney(r.rev) + "</td>" +
          "<td class='num'>" + fmtPct(r.rev ? r.margin / r.rev * 100 : null, 1) + "</td></tr>";
      }).join("") || "<tr><td colspan=4 class='empty'>No sales for this filter</td></tr>") + "</tbody>";
  }

  initFilters();
  loadHistory();
  loadPeriod();
})();

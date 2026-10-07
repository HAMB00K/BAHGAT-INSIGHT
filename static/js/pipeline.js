/* Data Pipeline page */
(function () {
  async function load() {
    var st = await getJSON("/api/pipeline_status");

    // KPI tiles
    var totalRaw = 0;
    if (st.manifest.files) {
      Object.values(st.manifest.files).forEach(function (f) { totalRaw += f.rows; });
    }
    var fixed = st.dq_log.reduce(function (a, d) { return a + (d.rows_affected || 0); }, 0);
    var totalStage = st.runs.find(function (r) { return r.stage === "TOTAL"; });
    document.getElementById("pipeKpis").innerHTML =
      '<div class="card"><div class="kpi-label">Raw rows ingested</div>' +
      '<div class="kpi-value">' + fmtInt(totalRaw) + "</div>" +
      '<span class="card-note">across 9 source files</span></div>' +
      '<div class="card"><div class="kpi-label">Quality issues handled</div>' +
      '<div class="kpi-value">' + fmtInt(fixed) + "</div>" +
      '<span class="card-note">deduplicated, repaired, normalised or quarantined</span></div>' +
      '<div class="card"><div class="kpi-label">Warehouse size</div>' +
      '<div class="kpi-value">' + st.db_size_mb + " MB</div>" +
      '<span class="card-note">SQLite · loaded in ' +
      (totalStage ? totalStage.seconds + "s" : "-") + "</span></div>";

    // DQ table
    document.getElementById("dqTable").innerHTML =
      "<thead><tr><th>Issue detected</th><th class='num'>Rows</th><th>Action taken</th></tr></thead><tbody>" +
      st.dq_log.map(function (d) {
        return "<tr><td>" + d.issue + "</td><td class='num'>" + fmtInt(d.rows_affected) +
               "</td><td class='sub'>" + d.action + "</td></tr>";
      }).join("") + "</tbody>";

    // warehouse tables
    document.getElementById("tblTable").innerHTML =
      "<thead><tr><th>Table</th><th class='num'>Rows</th></tr></thead><tbody>" +
      Object.keys(st.tables).map(function (t) {
        return "<tr><td><code>" + t + "</code></td><td class='num'>" +
               (st.tables[t] === null ? "–" : fmtInt(st.tables[t])) + "</td></tr>";
      }).join("") + "</tbody>";

    // stage timings
    document.getElementById("runTable").innerHTML =
      "<thead><tr><th>Stage</th><th class='num'>Seconds</th><th class='num'>Rows out</th></tr></thead><tbody>" +
      st.runs.map(function (r) {
        return "<tr><td>" + (r.stage === "TOTAL" ? "<b>TOTAL</b>" : r.stage) + "</td>" +
               "<td class='num'>" + r.seconds + "</td>" +
               "<td class='num'>" + fmtInt(r.rows_out) + "</td></tr>";
      }).join("") + "</tbody>";

    // manifest files
    var files = st.manifest.files || {};
    document.getElementById("fileTable").innerHTML =
      "<thead><tr><th>File</th><th class='num'>Rows</th><th class='num'>Size (MB)</th></tr></thead><tbody>" +
      Object.keys(files).map(function (f) {
        return "<tr><td><code>" + f + "</code></td><td class='num'>" + fmtInt(files[f].rows) +
               "</td><td class='num'>" + files[f].size_mb + "</td></tr>";
      }).join("") + "</tbody>";
  }

  load();
})();

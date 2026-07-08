// ===============================
// PneumoAI Analytics
// ===============================

const token = localStorage.getItem("accessToken");
const user  = JSON.parse(localStorage.getItem("user") || "{}");

document.addEventListener("DOMContentLoaded", () => {
    if (!token) { window.location.href = "/"; return; }
    initAvatar();
    bindLogout();
    loadAnalytics();
});

// ===============================
// Avatar
// ===============================
function initAvatar() {
    const avatar = document.querySelector(".topbar-avatar");
    if (!avatar) return;
    const name = user.fullName || user.username || "U";
    const initials = name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();
    const colors = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"];
    avatar.textContent = initials;
    avatar.style.background = colors[initials.charCodeAt(0) % colors.length];
}

// ===============================
// Logout
// ===============================
function bindLogout() {
    document.getElementById("logoutBtn")?.addEventListener("click", async (e) => {
        e.preventDefault();
        try {
            await fetch("/api/auth/logout", {
                method: "POST",
                headers: { Authorization: "Bearer " + token }
            });
        } catch (err) { console.error(err); }
        localStorage.clear();
        window.location.href = "/";
    });
}

// ===============================
// Load Analytics
// ===============================
let allReports = [];
let trendChart = null;
let donutChart = null;

async function loadAnalytics() {
    try {
        const res = await fetch("/api/dashboard/stats", {
            headers: { Authorization: "Bearer " + token }
        });

        if (res.status === 401) {
            localStorage.clear();
            window.location.href = "/";
            return;
        }

        const data = await res.json();

        updateSummary(data);
        renderCharts(data);
        allReports = data.recentScans || [];
        renderTable(allReports);
        bindSearch();

    } catch (err) {
        console.error("Analytics error:", err);
    }
}

// ===============================
// Summary Cards
// ===============================
function updateSummary(data) {
    document.getElementById("totalScans").textContent    = data.totalScans ?? 0;
    document.getElementById("healthyCases").textContent  = data.healthyCases ?? 0;
    document.getElementById("pneumoniaCases").textContent = data.pneumoniaCases ?? 0;
    document.getElementById("avgConfidence").textContent  = (data.averageConfidence ?? 0) + "%";
}

// ===============================
// Charts
// ===============================
function renderCharts(data) {

    // ── Trend Chart (Line) ──
    const trendEl = document.getElementById("trendChart");
    trendEl.innerHTML = '<canvas id="trendCanvas" height="280"></canvas>';
    const trendCtx = document.getElementById("trendCanvas").getContext("2d");

    // Group recent scans by date
    const grouped = {};
    (data.recentScans || []).forEach(scan => {
        const date = new Date(scan.predictionDate).toLocaleDateString("en", { month: "short", day: "numeric" });
        if (!grouped[date]) grouped[date] = { normal: 0, pneumonia: 0 };
        if (scan.detectedDisease && scan.detectedDisease.toUpperCase() === "PNEUMONIA") grouped[date].pneumonia++;
        else grouped[date].normal++;
    });

    const labels        = Object.keys(grouped).length ? Object.keys(grouped) : ["No Data"];
    const normalData    = Object.values(grouped).map(v => v.normal);
    const pneumoniaData = Object.values(grouped).map(v => v.pneumonia);

    if (trendChart) trendChart.destroy();
    trendChart = new Chart(trendCtx, {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: "Normal",
                    data: normalData,
                    borderColor: "#4f8ef7",
                    backgroundColor: "rgba(79,142,247,0.1)",
                    fill: true, tension: 0.4,
                    pointBackgroundColor: "#4f8ef7", pointRadius: 5,
                },
                {
                    label: "Pneumonia",
                    data: pneumoniaData,
                    borderColor: "#ff4757",
                    backgroundColor: "rgba(255,71,87,0.1)",
                    fill: true, tension: 0.4,
                    pointBackgroundColor: "#ff4757", pointRadius: 5,
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: "rgba(255,255,255,0.6)", font: { size: 12 } }
                }
            },
            scales: {
                x: {
                    grid: { color: "rgba(255,255,255,0.05)" },
                    ticks: { color: "rgba(255,255,255,0.4)", font: { size: 11 } }
                },
                y: {
                    grid: { color: "rgba(255,255,255,0.05)" },
                    ticks: { color: "rgba(255,255,255,0.4)", font: { size: 11 }, stepSize: 1 },
                    beginAtZero: true
                }
            }
        }
    });

    // ── Distribution Chart (Donut) ──
    const distEl = document.getElementById("distributionChart");
    distEl.innerHTML = `
        <div style="position:relative;width:220px;height:220px;margin:0 auto 16px">
            <canvas id="donutCanvas"></canvas>
            <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center">
                <div style="font-size:28px;font-weight:700;color:#fff">${data.totalScans ?? 0}</div>
                <div style="font-size:11px;color:rgba(255,255,255,0.4)">Total</div>
            </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:10px;padding:0 8px">
            <div style="display:flex;justify-content:space-between;font-size:13px">
                <span style="display:flex;align-items:center;gap:8px;color:rgba(255,255,255,0.6)">
                    <span style="width:10px;height:10px;border-radius:50%;background:#00d4aa;display:inline-block"></span>Normal
                </span>
                <strong style="color:#fff">${data.healthyPercentage ?? 0}%</strong>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:13px">
                <span style="display:flex;align-items:center;gap:8px;color:rgba(255,255,255,0.6)">
                    <span style="width:10px;height:10px;border-radius:50%;background:#ff4757;display:inline-block"></span>Pneumonia
                </span>
                <strong style="color:#fff">${data.pneumoniaPercentage ?? 0}%</strong>
            </div>
        </div>`;

    const donutCtx = document.getElementById("donutCanvas").getContext("2d");
    const total = data.totalScans || 0;

    if (donutChart) donutChart.destroy();
    donutChart = new Chart(donutCtx, {
        type: "doughnut",
        data: {
            labels: ["Normal", "Pneumonia"],
            datasets: [{
                data: total > 0 ? [data.healthyCases, data.pneumoniaCases] : [1, 0],
                backgroundColor: total > 0
                    ? ["#00d4aa", "#ff4757"]
                    : ["rgba(255,255,255,0.06)", "rgba(255,255,255,0.06)"],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            cutout: "72%",
            plugins: { legend: { display: false }, tooltip: { enabled: total > 0 } },
            responsive: true
        }
    });
}

// ===============================
// Table
// ===============================
function renderTable(reports) {
    const tbody = document.getElementById("reportTable");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (reports.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;opacity:0.5;padding:32px">No reports found</td></tr>`;
        return;
    }

    reports.forEach(r => {
        const isPneumonia = r.detectedDisease && r.detectedDisease.toUpperCase() === "PNEUMONIA";
        tbody.innerHTML += `
        <tr>
            <td>${r.patientName}</td>
            <td>
                <span style="padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;
                    ${isPneumonia
                        ? 'background:rgba(255,71,87,0.12);color:#ff4757;border:1px solid rgba(255,71,87,0.25)'
                        : 'background:rgba(0,212,170,0.12);color:#00d4aa;border:1px solid rgba(0,212,170,0.25)'}">
                    ${r.detectedDisease}
                </span>
            </td>
            <td style="color:${isPneumonia ? '#ff4757' : '#00d4aa'};font-weight:600">${r.confidence}%</td>
            <td>${new Date(r.predictionDate).toLocaleDateString("en", {month:"short",day:"2-digit",year:"numeric"})}</td>
            <td><button class="view-btn" onclick="window.location.href='/history'">View</button></td>
        </tr>`;
    });
}

// ===============================
// Search
// ===============================
function bindSearch() {
    document.getElementById("searchReport")?.addEventListener("input", function() {
        const q = this.value.toLowerCase();
        const filtered = allReports.filter(r =>
            r.patientName.toLowerCase().includes(q) ||
            r.detectedDisease.toLowerCase().includes(q)
        );
        renderTable(filtered);
    });
}
let currentFilters = {
    year: '2026',
    month: 'ALL',
    division: 'ALL',
    department: 'ALL',
    thresholdOnly: false
};

let chartInstances = {};

document.addEventListener('DOMContentLoaded', () => {
    initFilters();
    initTabs();
    initThemeToggle();
    initExportBtn();
    renderDashboard();
});

function initFilters() {
    const yearSelect = document.getElementById('filter-year');
    const monthSelect = document.getElementById('filter-month');
    const divisionSelect = document.getElementById('filter-division');
    const deptSelect = document.getElementById('filter-department');
    const thresholdCheck = document.getElementById('filter-variance-threshold');
    const resetBtn = document.getElementById('btn-reset-filters');

    const months = [...new Set(FINANCIAL_DATA.dates.map(d => d.month_name))];
    months.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        monthSelect.appendChild(opt);
    });

    const divisions = [...new Set(FINANCIAL_DATA.departments.map(d => d.division))];
    divisions.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d;
        opt.textContent = d;
        divisionSelect.appendChild(opt);
    });

    const depts = [...new Set(FINANCIAL_DATA.departments.map(d => d.department_name))];
    depts.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d;
        opt.textContent = d;
        deptSelect.appendChild(opt);
    });

    yearSelect.addEventListener('change', (e) => {
        currentFilters.year = e.target.value;
        renderDashboard();
    });

    monthSelect.addEventListener('change', (e) => {
        currentFilters.month = e.target.value;
        renderDashboard();
    });

    divisionSelect.addEventListener('change', (e) => {
        currentFilters.division = e.target.value;
        renderDashboard();
    });

    deptSelect.addEventListener('change', (e) => {
        currentFilters.department = e.target.value;
        renderDashboard();
    });

    thresholdCheck.addEventListener('change', (e) => {
        currentFilters.thresholdOnly = e.target.checked;
        renderDashboard();
    });

    resetBtn.addEventListener('click', () => {
        yearSelect.value = '2026';
        monthSelect.value = 'ALL';
        divisionSelect.value = 'ALL';
        deptSelect.value = 'ALL';
        thresholdCheck.checked = false;
        currentFilters = { year: '2026', month: 'ALL', division: 'ALL', department: 'ALL', thresholdOnly: false };
        renderDashboard();
    });
}

function initTabs() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const titles = {
        'overview': { title: 'Executive P&L Variance Overview', subtitle: 'MySQL Star Schema Real-Time Financial Aggregation' },
        'drilldown': { title: 'P&L Hierarchy Drill-Down Matrix', subtitle: 'Interactive GL Account Multi-Level Breakdown' },
        'ytd-mom': { title: 'YTD & MoM Financial Intelligence', subtitle: 'Cumulative Progression and Month-over-Month Velocity' },
        'exceptions': { title: 'Variance Exception & Audit Log', subtitle: 'Automated Flagging for Variances Exceeding \u00B110% Tolerance' }
    };

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            navItems.forEach(n => n.classList.remove('active'));
            tabContents.forEach(t => t.classList.remove('active'));
            item.classList.add('active');
            const targetElement = document.getElementById(`tab-${targetTab}`);
            if (targetElement) {
                targetElement.classList.add('active');
            }

            document.getElementById('page-title').textContent = titles[targetTab].title;
            document.getElementById('page-subtitle').textContent = titles[targetTab].subtitle;

            if (targetTab === 'drilldown') {
                renderDrillDownMatrix();
            } else if (targetTab === 'ytd-mom') {
                renderTimeIntelligence();
            } else if (targetTab === 'exceptions') {
                renderExceptionsTable();
            } else if (targetTab === 'overview') {
                renderCharts();
            }
        });
    });

    document.getElementById('btn-expand-all').addEventListener('click', () => {
        document.querySelectorAll('.tree-child').forEach(row => row.style.display = 'table-row');
        document.querySelectorAll('.tree-toggle-icon').forEach(icon => icon.textContent = '▼');
    });

    document.getElementById('btn-collapse-all').addEventListener('click', () => {
        document.querySelectorAll('.tree-level-1, .tree-level-2').forEach(row => row.style.display = 'none');
        document.querySelectorAll('.tree-toggle-icon').forEach(icon => icon.textContent = '►');
    });
}

function initThemeToggle() {
    const toggle = document.getElementById('theme-toggle');
    const label = document.getElementById('theme-label');
    toggle.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');
        const isLight = document.body.classList.contains('light-theme');
        label.textContent = isLight ? 'Light Mode' : 'Dark Mode';
        renderCharts();
    });
}

function getFilteredData() {
    return FINANCIAL_DATA.records.filter(r => {
        if (currentFilters.year !== 'ALL' && String(r.year) !== String(currentFilters.year)) return false;
        if (currentFilters.month !== 'ALL' && r.month_name !== currentFilters.month) return false;
        if (currentFilters.division !== 'ALL' && r.division !== currentFilters.division) return false;
        if (currentFilters.department !== 'ALL' && r.department_name !== currentFilters.department) return false;
        return true;
    });
}

function formatCurrency(val) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
}

function formatPct(val) {
    const sign = val > 0 ? '+' : '';
    return sign + (val * 100).toFixed(1) + '%';
}

function renderDashboard() {
    renderKPIs();
    renderCharts();
    renderDrillDownMatrix();
    renderTimeIntelligence();
    renderExceptionsTable();
}

function renderKPIs() {
    const data = getFilteredData();

    let revAct = 0, revBud = 0;
    let expAct = 0, expBud = 0;

    data.forEach(r => {
        const amt = parseFloat(r.amount);
        if (r.statement_section === 'Revenue') {
            if (r.scenario === 'Actual') revAct += amt;
            else if (r.scenario === 'Budget') revBud += amt;
        } else {
            if (r.scenario === 'Actual') expAct += amt;
            else if (r.scenario === 'Budget') expBud += amt;
        }
    });

    const netAct = revAct - expAct;
    const netBud = revBud - expBud;

    const revVar = revAct - revBud;
    const revVarPct = revBud !== 0 ? revVar / revBud : 0;

    const expVar = expAct - expBud;
    const expVarPct = expBud !== 0 ? expVar / expBud : 0;

    const netVar = netAct - netBud;
    const netVarPct = netBud !== 0 ? netVar / Math.abs(netBud) : 0;

    document.getElementById('kpi-act-revenue').textContent = formatCurrency(revAct);
    document.getElementById('kpi-bud-revenue').textContent = formatCurrency(revBud);
    const revBadge = document.getElementById('kpi-var-rev-badge');
    revBadge.textContent = formatPct(revVarPct);
    revBadge.className = `variance-badge ${revVar >= 0 ? 'favorable' : 'unfavorable'}`;
    document.getElementById('kpi-var-rev-diff').textContent = formatCurrency(revVar) + ' var';

    document.getElementById('kpi-act-expense').textContent = formatCurrency(expAct);
    document.getElementById('kpi-bud-expense').textContent = formatCurrency(expBud);
    const expBadge = document.getElementById('kpi-var-exp-badge');
    expBadge.textContent = formatPct(expVarPct);
    expBadge.className = `variance-badge ${expVar <= 0 ? 'favorable' : 'unfavorable'}`;
    document.getElementById('kpi-var-exp-diff').textContent = formatCurrency(expVar) + ' var';

    document.getElementById('kpi-act-profit').textContent = formatCurrency(netAct);
    document.getElementById('kpi-bud-profit').textContent = formatCurrency(netBud);
    const profitBadge = document.getElementById('kpi-var-profit-badge');
    profitBadge.textContent = formatPct(netVarPct);
    profitBadge.className = `variance-badge ${netVar >= 0 ? 'favorable' : 'unfavorable'}`;
    document.getElementById('kpi-var-profit-diff').textContent = formatCurrency(netVar) + ' var';

    const exceptions = computeExceptions(data);
    document.getElementById('kpi-alert-count').textContent = exceptions.length;
    document.getElementById('nav-alert-count').textContent = exceptions.length;
}

function computeExceptions(data) {
    const map = {};
    data.forEach(r => {
        const key = `${r.year}|${r.month_num}|${r.month_name}|${r.department_name}|${r.account_number}|${r.account_name}|${r.statement_section}`;
        if (!map[key]) {
            map[key] = { actual: 0, budget: 0, meta: r };
        }
        if (r.scenario === 'Actual') map[key].actual += parseFloat(r.amount);
        else if (r.scenario === 'Budget') map[key].budget += parseFloat(r.amount);
    });

    const exceptions = [];
    Object.keys(map).forEach(k => {
        const item = map[k];
        const diff = item.actual - item.budget;
        const pct = item.budget !== 0 ? diff / item.budget : 0;
        if (Math.abs(pct) >= 0.10) {
            exceptions.push({
                ...item.meta,
                actual: item.actual,
                budget: item.budget,
                variance: diff,
                variancePct: pct
            });
        }
    });
    return exceptions;
}

function renderCharts() {
    const data = getFilteredData();
    const isLight = document.body.classList.contains('light-theme');
    const textColor = isLight ? '#475569' : '#94A3B8';
    const gridColor = isLight ? 'rgba(0,0,0,0.06)' : 'rgba(255,255,255,0.06)';

    const monthsMap = {};
    data.forEach(r => {
        const mKey = r.month_short;
        const mOrder = parseInt(r.month_num);
        if (!monthsMap[mKey]) {
            monthsMap[mKey] = { order: mOrder, name: mKey, revAct: 0, revBud: 0, expAct: 0, expBud: 0 };
        }
        const amt = parseFloat(r.amount);
        if (r.statement_section === 'Revenue') {
            if (r.scenario === 'Actual') monthsMap[mKey].revAct += amt;
            else monthsMap[mKey].revBud += amt;
        } else {
            if (r.scenario === 'Actual') monthsMap[mKey].expAct += amt;
            else monthsMap[mKey].expBud += amt;
        }
    });

    const sortedMonths = Object.values(monthsMap).sort((a, b) => a.order - b.order);
    const monthLabels = sortedMonths.map(m => m.name);

    if (chartInstances.rev) chartInstances.rev.destroy();
    const ctxRev = document.getElementById('chart-revenue-trend').getContext('2d');
    chartInstances.rev = new Chart(ctxRev, {
        type: 'bar',
        data: {
            labels: monthLabels,
            datasets: [
                {
                    label: 'Budget Revenue',
                    data: sortedMonths.map(m => m.revBud),
                    backgroundColor: 'rgba(59, 130, 246, 0.35)',
                    borderColor: '#3B82F6',
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    type: 'line',
                    label: 'Actual Revenue',
                    data: sortedMonths.map(m => m.revAct),
                    borderColor: '#10B981',
                    backgroundColor: '#10B981',
                    borderWidth: 3,
                    tension: 0.3,
                    pointRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: textColor } } },
            scales: {
                x: { ticks: { color: textColor }, grid: { color: gridColor } },
                y: { ticks: { color: textColor, callback: v => '$' + (v / 1000) + 'k' }, grid: { color: gridColor } }
            }
        }
    });

    if (chartInstances.exp) chartInstances.exp.destroy();
    const ctxExp = document.getElementById('chart-expense-trend').getContext('2d');
    chartInstances.exp = new Chart(ctxExp, {
        type: 'bar',
        data: {
            labels: monthLabels,
            datasets: [
                {
                    label: 'Budget Expenses',
                    data: sortedMonths.map(m => m.expBud),
                    backgroundColor: 'rgba(245, 158, 11, 0.3)',
                    borderColor: '#F59E0B',
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    type: 'line',
                    label: 'Actual Expenses',
                    data: sortedMonths.map(m => m.expAct),
                    borderColor: '#EF4444',
                    backgroundColor: '#EF4444',
                    borderWidth: 3,
                    tension: 0.3,
                    pointRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: textColor } } },
            scales: {
                x: { ticks: { color: textColor }, grid: { color: gridColor } },
                y: { ticks: { color: textColor, callback: v => '$' + (v / 1000) + 'k' }, grid: { color: gridColor } }
            }
        }
    });

    const deptMap = {};
    data.forEach(r => {
        const d = r.department_name;
        if (!deptMap[d]) deptMap[d] = { actual: 0, budget: 0 };
        const amt = parseFloat(r.amount);
        if (r.scenario === 'Actual') deptMap[d].actual += amt;
        else deptMap[d].budget += amt;
    });

    const deptLabels = Object.keys(deptMap);
    const deptVariances = deptLabels.map(d => deptMap[d].actual - deptMap[d].budget);
    const deptColors = deptVariances.map(v => v >= 0 ? '#EF4444' : '#10B981');

    if (chartInstances.dept) chartInstances.dept.destroy();
    const ctxDept = document.getElementById('chart-dept-variance').getContext('2d');
    chartInstances.dept = new Chart(ctxDept, {
        type: 'bar',
        data: {
            labels: deptLabels,
            datasets: [{
                label: 'Variance ($)',
                data: deptVariances,
                backgroundColor: deptColors,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: textColor, callback: v => '$' + (v / 1000) + 'k' }, grid: { color: gridColor } },
                y: { ticks: { color: textColor }, grid: { color: gridColor } }
            }
        }
    });

    const secMap = { 'Revenue': 0, 'COGS': 0, 'OPEX': 0 };
    data.forEach(r => {
        const amt = parseFloat(r.amount);
        const diff = r.scenario === 'Actual' ? amt : -amt;
        if (secMap[r.statement_section] !== undefined) {
            secMap[r.statement_section] += diff;
        }
    });

    const secLabels = ['Revenue Variance', 'COGS Variance', 'OPEX Variance'];
    const secVals = [secMap['Revenue'], -secMap['COGS'], -secMap['OPEX']];
    const secColors = [
        secVals[0] >= 0 ? '#10B981' : '#EF4444',
        secVals[1] >= 0 ? '#10B981' : '#EF4444',
        secVals[2] >= 0 ? '#10B981' : '#EF4444'
    ];

    if (chartInstances.sec) chartInstances.sec.destroy();
    const ctxSec = document.getElementById('chart-section-waterfall').getContext('2d');
    chartInstances.sec = new Chart(ctxSec, {
        type: 'bar',
        data: {
            labels: secLabels,
            datasets: [{
                label: 'Net P&L Impact ($)',
                data: secVals,
                backgroundColor: secColors,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: textColor }, grid: { color: gridColor } },
                y: { ticks: { color: textColor, callback: v => '$' + (v / 1000) + 'k' }, grid: { color: gridColor } }
            }
        }
    });
}

function renderDrillDownMatrix() {
    const data = getFilteredData();
    const tbody = document.getElementById('matrix-drilldown-body');
    tbody.innerHTML = '';

    const hierarchy = {};

    data.forEach(r => {
        const dept = r.department_name;
        const sec = r.statement_section;
        const acct = `${r.account_number} - ${r.account_name}`;

        if (!hierarchy[dept]) hierarchy[dept] = { actual: 0, budget: 0, sections: {} };
        if (!hierarchy[dept].sections[sec]) hierarchy[dept].sections[sec] = { actual: 0, budget: 0, accounts: {} };
        if (!hierarchy[dept].sections[sec].accounts[acct]) hierarchy[dept].sections[sec].accounts[acct] = { actual: 0, budget: 0 };

        const amt = parseFloat(r.amount);
        if (r.scenario === 'Actual') {
            hierarchy[dept].actual += amt;
            hierarchy[dept].sections[sec].actual += amt;
            hierarchy[dept].sections[sec].accounts[acct].actual += amt;
        } else {
            hierarchy[dept].budget += amt;
            hierarchy[dept].sections[sec].budget += amt;
            hierarchy[dept].sections[sec].accounts[acct].budget += amt;
        }
    });

    let deptIdx = 0;
    Object.keys(hierarchy).sort().forEach(dept => {
        deptIdx++;
        const deptNode = hierarchy[dept];
        const deptVar = deptNode.actual - deptNode.budget;
        const deptPct = deptNode.budget !== 0 ? deptVar / deptNode.budget : 0;
        const deptRowId = `dept-row-${deptIdx}`;

        const trDept = document.createElement('tr');
        trDept.className = 'tree-row tree-level-0';
        trDept.innerHTML = `
            <td><span class="tree-toggle-icon" id="toggle-${deptRowId}">▼</span> ${dept}</td>
            <td>${formatCurrency(deptNode.actual)}</td>
            <td>${formatCurrency(deptNode.budget)}</td>
            <td style="color: ${deptVar <= 0 ? 'var(--color-favorable)' : 'var(--color-unfavorable)'}">${formatCurrency(deptVar)}</td>
            <td>${formatPct(deptPct)}</td>
            <td><span class="audit-badge-pill ${Math.abs(deptPct) >= 0.10 ? 'pill-alert' : 'pill-ok'}">${Math.abs(deptPct) >= 0.10 ? 'FLAGGED' : 'ON TRACK'}</span></td>
        `;
        tbody.appendChild(trDept);

        let secIdx = 0;
        Object.keys(deptNode.sections).sort().forEach(sec => {
            secIdx++;
            const secNode = deptNode.sections[sec];
            const secVar = secNode.actual - secNode.budget;
            const secPct = secNode.budget !== 0 ? secVar / secNode.budget : 0;
            const secRowId = `${deptRowId}-sec-${secIdx}`;

            const trSec = document.createElement('tr');
            trSec.className = `tree-row tree-child tree-level-1 ${deptRowId}`;
            trSec.innerHTML = `
                <td><span class="tree-toggle-icon" id="toggle-${secRowId}">▼</span> ${sec}</td>
                <td>${formatCurrency(secNode.actual)}</td>
                <td>${formatCurrency(secNode.budget)}</td>
                <td>${formatCurrency(secVar)}</td>
                <td>${formatPct(secPct)}</td>
                <td><span class="audit-badge-pill ${Math.abs(secPct) >= 0.10 ? 'pill-alert' : 'pill-ok'}">${Math.abs(secPct) >= 0.10 ? 'FLAGGED' : 'ON TRACK'}</span></td>
            `;
            tbody.appendChild(trSec);

            Object.keys(secNode.accounts).sort().forEach(acct => {
                const acctNode = secNode.accounts[acct];
                const acctVar = acctNode.actual - acctNode.budget;
                const acctPct = acctNode.budget !== 0 ? acctVar / acctNode.budget : 0;

                const trAcct = document.createElement('tr');
                trAcct.className = `tree-child tree-level-2 ${deptRowId} ${secRowId}`;
                trAcct.innerHTML = `
                    <td>${acct}</td>
                    <td>${formatCurrency(acctNode.actual)}</td>
                    <td>${formatCurrency(acctNode.budget)}</td>
                    <td>${formatCurrency(acctVar)}</td>
                    <td>${formatPct(acctPct)}</td>
                    <td><span class="audit-badge-pill ${Math.abs(acctPct) >= 0.10 ? 'pill-alert' : 'pill-ok'}">${Math.abs(acctPct) >= 0.10 ? 'FLAGGED (>10%)' : 'NORMAL'}</span></td>
                `;
                tbody.appendChild(trAcct);
            });

            trSec.addEventListener('click', (e) => {
                const isCollapsed = trSec.querySelector('.tree-toggle-icon').textContent === '►';
                trSec.querySelector('.tree-toggle-icon').textContent = isCollapsed ? '▼' : '►';
                document.querySelectorAll(`.${secRowId}`).forEach(r => {
                    r.style.display = isCollapsed ? 'table-row' : 'none';
                });
            });
        });

        trDept.addEventListener('click', (e) => {
            const isCollapsed = trDept.querySelector('.tree-toggle-icon').textContent === '►';
            trDept.querySelector('.tree-toggle-icon').textContent = isCollapsed ? '▼' : '►';
            document.querySelectorAll(`.${deptRowId}`).forEach(r => {
                r.style.display = isCollapsed ? 'table-row' : 'none';
            });
        });
    });
}

function renderTimeIntelligence() {
    const data = getFilteredData();
    const tbody = document.getElementById('body-time-intel');
    tbody.innerHTML = '';

    const monthsMap = {};
    data.forEach(r => {
        const ym = r.year_month;
        const ord = r.year * 100 + parseInt(r.month_num);
        if (!monthsMap[ym]) {
            monthsMap[ym] = { ym, ord, month_name: r.month_name, actual: 0, budget: 0 };
        }
        const amt = parseFloat(r.amount);
        if (r.scenario === 'Actual') monthsMap[ym].actual += amt;
        else monthsMap[ym].budget += amt;
    });

    const sorted = Object.values(monthsMap).sort((a, b) => a.ord - b.ord);

    let cumAct = 0;
    let cumBud = 0;
    let prevAct = null;

    const ytdLabels = [];
    const ytdActList = [];
    const ytdBudList = [];

    sorted.forEach(row => {
        cumAct += row.actual;
        cumBud += row.budget;

        const diff = row.actual - row.budget;
        const momGrowth = prevAct !== null && prevAct !== 0 ? (row.actual - prevAct) / prevAct : 0;
        const ytdPct = cumBud !== 0 ? (cumAct - cumBud) / cumBud : 0;

        ytdLabels.push(row.ym);
        ytdActList.push(cumAct);
        ytdBudList.push(cumBud);

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${row.ym}</strong> (${row.month_name})</td>
            <td>${formatCurrency(row.actual)}</td>
            <td>${formatCurrency(row.budget)}</td>
            <td style="color: ${diff <= 0 ? 'var(--color-favorable)' : 'var(--color-unfavorable)'}">${formatCurrency(diff)}</td>
            <td>${prevAct !== null ? formatPct(momGrowth) : '-'}</td>
            <td><strong>${formatCurrency(cumAct)}</strong></td>
            <td>${formatCurrency(cumBud)}</td>
            <td><span class="audit-badge-pill ${Math.abs(ytdPct) >= 0.10 ? 'pill-alert' : 'pill-ok'}">${formatPct(ytdPct)}</span></td>
        `;
        tbody.appendChild(tr);
        prevAct = row.actual;
    });

    const isLight = document.body.classList.contains('light-theme');
    const textColor = isLight ? '#475569' : '#94A3B8';
    const gridColor = isLight ? 'rgba(0,0,0,0.06)' : 'rgba(255,255,255,0.06)';

    if (chartInstances.ytd) chartInstances.ytd.destroy();
    const ctxYtd = document.getElementById('chart-ytd-cumulative').getContext('2d');
    chartInstances.ytd = new Chart(ctxYtd, {
        type: 'line',
        data: {
            labels: ytdLabels,
            datasets: [
                {
                    label: 'Cumulative Actuals YTD ($)',
                    data: ytdActList,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.2
                },
                {
                    label: 'Cumulative Budget YTD ($)',
                    data: ytdBudList,
                    borderColor: '#94A3B8',
                    borderWidth: 2,
                    borderDash: [6, 6],
                    fill: false,
                    tension: 0.2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: textColor } } },
            scales: {
                x: { ticks: { color: textColor }, grid: { color: gridColor } },
                y: { ticks: { color: textColor, callback: v => '$' + (v / 1000000).toFixed(1) + 'M' }, grid: { color: gridColor } }
            }
        }
    });
}

function renderExceptionsTable() {
    const data = getFilteredData();
    const tbody = document.getElementById('body-exceptions');
    tbody.innerHTML = '';

    const exceptions = computeExceptions(data);

    exceptions.sort((a, b) => Math.abs(b.variancePct) - Math.abs(a.variancePct));

    exceptions.forEach(ex => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${ex.year}-${String(ex.month_num).padStart(2, '0')}</strong></td>
            <td>${ex.department_name}</td>
            <td><code>${ex.account_number}</code></td>
            <td>${ex.account_name}</td>
            <td>${ex.statement_section}</td>
            <td>${formatCurrency(ex.actual)}</td>
            <td>${formatCurrency(ex.budget)}</td>
            <td style="color: ${ex.variance <= 0 && ex.statement_section !== 'Revenue' ? 'var(--color-favorable)' : 'var(--color-unfavorable)'}">${formatCurrency(ex.variance)}</td>
            <td><strong>${formatPct(ex.variancePct)}</strong></td>
            <td><span class="audit-badge-pill pill-alert">ACTION REQUIRED</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function initExportBtn() {
    document.getElementById('btn-export-csv').addEventListener('click', () => {
        const data = getFilteredData();
        if (!data || data.length === 0) return;

        const headers = Object.keys(data[0]);
        const csvRows = [headers.join(',')];

        data.forEach(r => {
            const values = headers.map(h => `"${r[h]}"`);
            csvRows.push(values.join(','));
        });

        const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `financial_variance_export_${currentFilters.year}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    });
}

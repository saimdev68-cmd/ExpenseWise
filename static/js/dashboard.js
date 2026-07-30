let barChart = null;
let donutChart = null;

// Exact color schemes matching your layout components
const brandColors = ['#6366f1', '#a855f7', '#f59e0b', '#c084fc', '#f43f5e', '#38bdf8', '#94a3b8'];

document.addEventListener("DOMContentLoaded", function() {
    initCharts();
    updateDashboardCharts('this_month'); // initial load trigger
});

function initCharts() {
    const ctxBar = document.getElementById('incomeExpenseChart').getContext('2d');
    barChart = new Chart(ctxBar, {
        type: 'bar',
        data: { labels: [], datasets: [] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false } },
                y: { border: { dash: [4, 4] }, grid: { color: '#e2e8f0' } }
            }
        }
    });

    const ctxDonut = document.getElementById('expenseCategoryChart').getContext('2d');
    donutChart = new Chart(ctxDonut, {
        type: 'doughnut',
        data: { labels: [], datasets: [] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: { legend: { display: false } }
        }
    });
}

function updateDashboardCharts(selectedPeriod) {
    // Keep both chart filter drop-downs perfectly synchronized
    document.querySelectorAll('.chart-filter-dropdown').forEach(dropdown => {
        dropdown.value = selectedPeriod;
    });

    // Request fresh metrics using explicit AJAX context parsing
    fetch(`/api/chart-data/?period=${selectedPeriod}`)
        .then(response => response.json())
        .then(data => {
            
            // 1. Refresh Left Bar Chart Data
            barChart.data.labels = data.bar_labels;
            barChart.data.datasets = [
                { label: 'Income', data: data.income_data, backgroundColor: '#6366f1', borderRadius: 4 },
                { label: 'Expense', data: data.expense_data, backgroundColor: '#f43f5e', borderRadius: 4 }
            ];
            barChart.update();

            // 2. Refresh Right Donut Chart Data
            donutChart.data.labels = data.donut_labels;
            donutChart.data.datasets = [{
                data: data.donut_data,
                backgroundColor: brandColors
            }];
            donutChart.update();

            // Update Inner Total Text Display Indicator
            document.getElementById('donutTotalAmount').innerText = '$' + data.donut_total.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});

            // 3. Render HTML Rows for Legend Interface Elements
            const legendContainer = document.getElementById('donutLegendRows');
            legendContainer.innerHTML = '';
            
            data.donut_labels.forEach((label, index) => {
                const amountStr = '$' + data.donut_data[index].toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0});
                const rowHTML = `
                    <div class="legend-item-row">
                        <div class="legend-left-side">
                            <div class="legend-color-dot" style="background-color: ${brandColors[index % brandColors.length]}"></div>
                            <span>${label}</span>
                        </div>
                        <div class="legend-right-side">
                            <span class="legend-amt">${amountStr}</span>
                            <span class="legend-pct">${data.donut_percentages[index]}%</span>
                        </div>
                    </div>
                `;
                legendContainer.insertAdjacentHTML('beforeend', rowHTML);
            });
        });
}
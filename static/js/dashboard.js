let barChart = null;
let donutChart = null;
let trendChart = null;

const brandColors = ['#6366f1', '#a855f7', '#f59e0b', '#c084fc', '#f43f5e', '#38bdf8', '#94a3b8'];

document.addEventListener("DOMContentLoaded", function() {
    initCharts();
    // Fetch initial data based on default dropdown selections
    updateChart('bar', 'this_month');
    updateChart('donut', 'this_month');
    updateChart('trend', 'last_6_months');
});

function initCharts() {
    // 1. Income vs Expense Bar Chart
    const ctxBar = document.getElementById('incomeExpenseChart').getContext('2d');
    barChart = new Chart(ctxBar, {
        type: 'bar',
        data: { labels: [], datasets: [] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: true, position: 'top', align: 'start' } },
            scales: {
                x: { grid: { display: false } },
                y: { border: { dash: [4, 4] }, grid: { color: '#e2e8f0' } }
            }
        }
    });

    // 2. Expense Categories Donut Chart
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

    // 3. Spending Trend Line Chart
    const ctxTrend = document.getElementById('spendingTrendChart').getContext('2d');
    
    // Create gradient for the line chart fill
    let gradientFill = ctxTrend.createLinearGradient(0, 0, 0, 300);
    gradientFill.addColorStop(0, 'rgba(168, 85, 247, 0.4)'); // Purple tint
    gradientFill.addColorStop(1, 'rgba(168, 85, 247, 0.0)'); 

    trendChart = new Chart(ctxTrend, {
        type: 'line',
        data: { labels: [], datasets: [] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            elements: {
                line: { tension: 0.4 }, // Smooth curves
                point: { radius: 4, backgroundColor: '#ffffff', borderWidth: 2, borderColor: '#a855f7' }
            },
            scales: {
                x: { grid: { display: false } },
                y: { border: { dash: [4, 4] }, grid: { color: '#e2e8f0' }, beginAtZero: true }
            }
        }
    });
}

function updateChart(chartType, selectedPeriod) {
    fetch(`/api/chart-data/?chart_type=${chartType}&period=${selectedPeriod}`)
        .then(response => response.json())
        .then(data => {
            if (chartType === 'bar') {
                barChart.data.labels = data.labels;
                barChart.data.datasets = [
                    { label: 'Income', data: data.income_data, backgroundColor: '#6366f1', borderRadius: 4 },
                    { label: 'Expense', data: data.expense_data, backgroundColor: '#f43f5e', borderRadius: 4 }
                ];
                barChart.update();

            } else if (chartType === 'donut') {
                donutChart.data.labels = data.labels;
                donutChart.data.datasets = [{
                    data: data.data,
                    backgroundColor: brandColors
                }];
                donutChart.update();

                document.getElementById('donutTotalAmount').innerText = 'Rs' + data.total.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0});

                const legendContainer = document.getElementById('donutLegendRows');
                legendContainer.innerHTML = '';
                
                data.labels.forEach((label, index) => {
                    const amountStr = 'Rs' + data.data[index].toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0});
                    const rowHTML = `
                        <div class="legend-item-row">
                            <div class="legend-left-side">
                                <div class="legend-color-dot" style="background-color: Rs{brandColors[index % brandColors.length]}"></div>
                                <span>${label}</span>
                            </div>
                            <div class="legend-right-side">
                                <span class="legend-amt">${amountStr}</span>
                                <span class="legend-pct">${data.percentages[index]}%</span>
                            </div>
                        </div>
                    `;
                    legendContainer.insertAdjacentHTML('beforeend', rowHTML);
                });

            } else if (chartType === 'trend') {
                let ctxTrend = document.getElementById('spendingTrendChart').getContext('2d');
                let gradientFill = ctxTrend.createLinearGradient(0, 0, 0, 300);
                gradientFill.addColorStop(0, 'rgba(168, 85, 247, 0.4)');
                gradientFill.addColorStop(1, 'rgba(168, 85, 247, 0.0)'); 

                trendChart.data.labels = data.labels;
                trendChart.data.datasets = [{
                    label: 'Spend',
                    data: data.data,
                    borderColor: '#a855f7',
                    backgroundColor: gradientFill,
                    borderWidth: 3,
                    fill: true
                }];
                trendChart.update();
            }
        });
}
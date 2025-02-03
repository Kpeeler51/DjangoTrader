// Function to create a chart using Chart.js
function createChart(dates, prices, symbol, currency) {
    // canvas context for rendering chart.
    const ctx = document.getElementById('stockChart').getContext('2d');
    // Creates a new chart instance.
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: `${symbol} (${currency})`,
                data: prices,
                borderColor: '#62AB37',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day'
                    },
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: `Price (${currency})`
                    }
                }
            }
        }
    });
}
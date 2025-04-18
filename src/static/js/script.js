document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('priceChart').getContext('2d');
    let chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Price (USD)',
                    data: [],
                    borderColor: '#00FF00',
                    backgroundColor: 'rgba(0, 255, 0, 0.1)',
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'RSI',
                    data: [],
                    borderColor: '#FF00FF',
                    backgroundColor: 'rgba(255, 0, 255, 0.1)',
                    fill: false,
                    yAxisID: 'y1'
                },
                {
                    label: 'Stochastic %K',
                    data: [],
                    borderColor: '#FFFF00',
                    backgroundColor: 'rgba(255, 255, 0, 0.1)',
                    fill: false,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: { display: true, title: { display: true, text: 'Time', color: '#00FF00' } },
                y: { 
                    display: true, 
                    title: { display: true, text: 'Price', color: '#00FF00' },
                    position: 'left'
                },
                y1: { 
                    display: true, 
                    title: { display: true, text: 'Indicator', color: '#00FF00' },
                    position: 'right',
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });

    function updateChart() {
        const period = document.querySelector('select[name="period"]').value;
        const asset = document.querySelector('select[name="asset"]').value;
        fetch(`/trades?period=${period}&asset=${asset}`)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const marketData = JSON.parse(doc.querySelector('#market-data').textContent);
                chart.data.labels = marketData.map(d => new Date(d.timestamp).toLocaleTimeString());
                chart.data.datasets[0].data = marketData.map(d => d.price);
                chart.data.datasets[1].data = marketData.map(d => d.rsi);
                chart.data.datasets[2].data = marketData.map(d => d.stoch_k);
                chart.update();
            })
            .catch(error => console.error('Error updating chart:', error));
    }

    updateChart();
    setInterval(updateChart, 60000);  // Update setiap 60 detik

    // Update chart saat filter berubah
    document.querySelector('select[name="period"]').addEventListener('change', updateChart);
    document.querySelector('select[name="asset"]').addEventListener('change', updateChart);
});
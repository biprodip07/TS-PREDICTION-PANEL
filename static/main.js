document.addEventListener('DOMContentLoaded', () => {
    // 1. Countdown Timer (1 Minute Periods)
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        setInterval(() => {
            const now = new Date();
            const secondsLeft = 60 - now.getSeconds();
            const formatted = `00:${secondsLeft < 10 ? '0' : ''}${secondsLeft}`;
            timerElement.textContent = formatted;
        }, 1000);
    }

    // 2. Fetch API Data (Auto Refresh every 5s)
    const fetchRecords = () => {
        const searchVal = document.getElementById('searchInput')?.value || '';
        fetch(`/api/records?search=${searchVal}`)
            .then(res => res.json())
            .then(data => {
                const tbody = document.getElementById('historyBody');
                if(!tbody) return;
                tbody.innerHTML = '';
                data.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.classList.add('fade-in');
                    tr.innerHTML = `
                        <td>${row.period}</td>
                        <td class="text-center font-weight-bold">${row.number}</td>
                        <td>${row.size}</td>
                        <td><span style="color: ${row.color.toLowerCase()}">${row.color}</span></td>
                        <td>${row.time}</td>
                    `;
                    tbody.appendChild(tr);
                });
            });

        fetch('/api/stats')
            .then(res => res.json())
            .then(data => {
                if(document.getElementById('totalHistory')) {
                    document.getElementById('totalHistory').innerText = data.total;
                    document.getElementById('totalWin').innerText = data.win;
                    document.getElementById('totalLoss').innerText = data.loss;
                }
            });
    };

    if (document.getElementById('historyBody')) {
        fetchRecords();
        setInterval(fetchRecords, 5000); // 5 second auto-refresh
        
        document.getElementById('searchInput').addEventListener('keyup', fetchRecords);
    }

    // 3. Initialize Chart.js (Admin Dashboard)
    const ctx = document.getElementById('statsChart');
    if (ctx) {
        fetch('/api/stats').then(res => res.json()).then(data => {
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Win', 'Loss'],
                    datasets: [{
                        data: [data.win, data.loss],
                        backgroundColor: ['#39ff14', '#ff3333'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#c9d1d9' } }
                    }
                }
            });
        });
    }
});

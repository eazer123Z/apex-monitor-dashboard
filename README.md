# apex-monitor-dashboard

Dashboard monitoring APEX-TITAN (private).

- `index.html` — halaman statis (Tailwind CDN + vanilla JS), fetch `data.json` tiap 30 detik.
- `data.json` — data paper trading (virtual) + status sistem, di-refresh otomatis tiap 5 menit.
- `update_data.py` — script refresh (jalan di VM via cron, bukan di Vercel).

Tidak ada API key, kredensial, atau data sensitif di repo ini.

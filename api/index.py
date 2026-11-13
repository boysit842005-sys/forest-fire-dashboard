from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Vercel Cloud Fire & Forest Degradation Monitoring Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_station_data = {
    "temperature": 0.0,
    "humidity": 0.0,
    "ppm": 0.0,
    "fire_probability": 0.0,
    "degradation_ha": 26478.8,
    "fire_now": False,
    "fire_risk": False,
    "status_text": "Đang chờ dữ liệu từ Laptop...",
    "updated_at": "--:--:--"
}

# Gộp tất cả đường dẫn vào một hàm duy nhất để chống lỗi 405 của Vercel
@app.api_route("/", methods=["GET", "POST"])
@app.api_route("/{path_name:path}", methods=["GET", "POST"])
async def catch_all_routes(request: Request):
    global latest_station_data
    
    # 1. Nếu Laptop gửi dữ liệu lên (Nhận diện bằng lệnh POST)
    if request.method == "POST":
        try:
            payload = await request.json()
            latest_station_data.update(payload)
            return {"status": "ok"}
        except Exception:
            return {"status": "error"}

    # 2. Nếu Giao diện Web muốn lấy số liệu (Nhận diện bằng đuôi ?data=1)
    if request.query_params.get("data") == "1":
        return JSONResponse(content=latest_station_data)
    
    # 3. Nếu người dùng mở link trên trình duyệt (Trả về giao diện Web)
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trạm Quan Trắc Cháy & Dự Báo Suy Giảm Rừng AI</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 25px; text-align: center; transition: background 0.3s; }
        body.fire-now { animation: flashRed 0.7s infinite; }
        body.fire-risk { background: #451a03; }
        @keyframes flashRed { 0%, 100% { background: #0f172a; } 50% { background: #991b1b; } }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(195px, 1fr)); gap: 16px; max-width: 1120px; margin: 25px auto; }
        .card { background: #1e293b; padding: 20px 16px; border-radius: 14px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2); }
        .card h3 { margin: 0 0 10px 0; color: #94a3b8; font-size: 0.95rem; }
        .val { font-size: 2.2rem; font-weight: bold; }
        .unit { font-size: 1.05rem; font-weight: normal; color: #cbd5e1; }
        .sub-note { font-size: 0.8rem; color: #64748b; margin-top: 6px; }

        .banner { max-width: 1080px; margin: 0 auto 28px auto; padding: 18px; border-radius: 12px; font-size: 1.25rem; font-weight: bold; background: #14532d; border: 2px solid #22c55e; }
        .banner.risk { background: #78350f; border-color: #f59e0b; color: #fef3c7; }
        .banner.now  { background: #7f1d1d; border-color: #ef4444; color: #ffffff; }

        .forecast-panel { max-width: 1120px; margin: 0 auto; background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 20px; }
        .forecast-panel h2 { margin: 0 0 6px 0; font-size: 1.2rem; color: #e2e8f0; }
        .forecast-panel p { margin: 0 0 16px 0; font-size: 0.9rem; color: #94a3b8; }
        .table-wrap { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
        th, td { padding: 10px 12px; border-bottom: 1px solid #334155; text-align: center; }
        th { background: #0f172a; color: #94a3b8; font-weight: 600; }
        tr:last-child td { border-bottom: none; }
        .loss-badge { color: #f87171; font-weight: bold; }
        .area-badge { color: #4ade80; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🌲 TRẠM QUAN TRẮC CHÁY & DỰ BÁO SUY GIẢM RỪNG AI</h1>
    <p style="color:#94a3b8">Cập nhật lúc: <span id="time">--</span></p>

    <div class="grid">
        <div class="card">
            <h3>🌡️ Nhiệt Độ (DHT11)</h3>
            <div class="val" style="color:#fb923c"><span id="temp">0.0</span> <span class="unit">°C</span></div>
            <div class="sub-note">Cảm biến nhiệt độ môi trường</div>
        </div>
        <div class="card">
            <h3>💧 Độ Ẩm (DHT11)</h3>
            <div class="val" style="color:#38bdf8"><span id="hum">0.0</span> <span class="unit">%</span></div>
            <div class="sub-note">Độ ẩm không khí thực tế</div>
        </div>
        <div class="card">
            <h3>💨 Khí Gas / Khói (MQ135)</h3>
            <div class="val" style="color:#c084fc"><span id="ppm">0</span> <span class="unit">ppm</span></div>
            <div class="sub-note">Nồng độ khí dễ cháy & khói</div>
        </div>
        <div class="card">
            <h3>🤖 Dự Báo Cháy (XGBoost)</h3>
            <div class="val" style="color:#facc15"><span id="prob">0.0</span> <span class="unit">%</span></div>
            <div class="sub-note">Xác suất bùng phát cháy</div>
        </div>
        <div class="card">
            <h3>📉 Suy Giảm Rừng (AI)</h3>
            <div class="val" style="color:#f87171">-<span id="degrad">26,479</span> <span class="unit">ha/năm</span></div>
            <div class="sub-note">Tốc độ mất rừng điều chỉnh rủi ro</div>
        </div>
    </div>

    <div id="banner" class="banner">
        Trạng thái: <span id="status">Đang kết nối...</span>
    </div>

    <div class="forecast-panel">
        <h2>📊 Dự Báo Quỹ Đạo Rừng Tự Nhiên Việt Nam Đến Năm 2030 (Mô hình XGBoost + Base Margin)</h2>
        <p>Độ chính xác tập Test: R² = 0.8221 | MAPE = 0.067% | Tổng suy giảm dự kiến (2025–2030): -146,536 ha</p>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Năm dự báo</th>
                        <th>Diện tích rừng tự nhiên (Triệu ha)</th>
                        <th>Tốc độ suy giảm nền (ha/năm)</th>
                        <th>Quán tính cơ sở (Base Margin)</th>
                        <th>Phần dư phi tuyến (XGBoost Residual)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>2026 (Hiện tại)</b></td>
                        <td class="area-badge">10.8330</td>
                        <td class="loss-badge">-26,479 ha</td>
                        <td>10.8342</td>
                        <td>-0.001186</td>
                    </tr>
                    <tr>
                        <td><b>2027</b></td>
                        <td class="area-badge">10.8051</td>
                        <td class="loss-badge">-27,893 ha</td>
                        <td>10.8065</td>
                        <td>-0.001414</td>
                    </tr>
                    <tr>
                        <td><b>2028</b></td>
                        <td class="area-badge">10.7758</td>
                        <td class="loss-badge">-29,307 ha</td>
                        <td>10.7772</td>
                        <td>-0.001414</td>
                    </tr>
                    <tr>
                        <td><b>2029</b></td>
                        <td class="area-badge">10.7451</td>
                        <td class="loss-badge">-30,722 ha</td>
                        <td>10.7465</td>
                        <td>-0.001414</td>
                    </tr>
                    <tr>
                        <td><b>2030</b></td>
                        <td class="area-badge">10.7130</td>
                        <td class="loss-badge">-32,136 ha</td>
                        <td>10.7144</td>
                        <td>-0.001414</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        async function loadData() {
            try {
                const res = await fetch('/?data=1');
                const d = await res.json();
                document.getElementById('temp').innerText = d.temperature;
                document.getElementById('hum').innerText = d.humidity;
                document.getElementById('ppm').innerText = d.ppm;
                document.getElementById('prob').innerText = d.fire_probability;
                
                const degVal = d.degradation_ha !== undefined ? Number(d.degradation_ha).toLocaleString('en-US', {maximumFractionDigits: 1}) : "26,478.8";
                document.getElementById('degrad').innerText = degVal;
                
                document.getElementById('time').innerText = d.updated_at;
                document.getElementById('status').innerText = d.status_text;

                const banner = document.getElementById('banner');
                document.body.className = ""; banner.className = "banner";

                if (d.fire_now) {
                    document.body.classList.add("fire-now"); banner.classList.add("now");
                } else if (d.fire_risk) {
                    document.body.classList.add("fire-risk"); banner.classList.add("risk");
                }
            } catch (e) { console.error(e); }
        }
        setInterval(loadData, 2000);
        loadData();
    </script>
</body>
</html>
    """)
# Cap nhat giao dien AI suy giam rung
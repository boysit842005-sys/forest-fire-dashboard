from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Vercel Cloud Fire Monitoring Server")

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
    "fire_now": False,
    "fire_risk": False,
    "status_text": "Đang chờ dữ liệu từ Laptop...",
    "updated_at": "--:--:--"
}

# Gộp tất cả đường dẫn vào một hàm duy nhất để chống lại bộ lọc của Vercel
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
        except:
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
    <title>Trạm Quan Trắc & Dự Báo Cháy Rừng Cloud</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 25px; text-align: center; transition: background 0.3s; }
        body.fire-now { animation: flashRed 0.7s infinite; }
        body.fire-risk { background: #451a03; }
        @keyframes flashRed { 0%, 100% { background: #0f172a; } 50% { background: #991b1b; } }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 18px; max-width: 980px; margin: 25px auto; }
        .card { background: #1e293b; padding: 22px; border-radius: 14px; border: 1px solid #334155; }
        .card h3 { margin: 0 0 10px 0; color: #94a3b8; font-size: 1rem; }
        .val { font-size: 2.5rem; font-weight: bold; }
        .banner { max-width: 940px; margin: 0 auto; padding: 18px; border-radius: 12px; font-size: 1.3rem; font-weight: bold; background: #14532d; border: 2px solid #22c55e; }
        .banner.risk { background: #78350f; border-color: #f59e0b; color: #fef3c7; }
        .banner.now  { background: #7f1d1d; border-color: #ef4444; color: #ffffff; }
    </style>
</head>
<body>
    <h1>🌲 TRẠM QUAN TRẮC & DỰ BÁO CHÁY RỪNG AI</h1>
    <p style="color:#94a3b8">Cập nhật lúc: <span id="time">--</span></p>

    <div class="grid">
        <div class="card"><h3>🌡️ Nhiệt Độ (DHT11)</h3><div class="val" style="color:#fb923c"><span id="temp">0.0</span> °C</div></div>
        <div class="card"><h3>💧 Độ Ẩm (DHT11)</h3><div class="val" style="color:#38bdf8"><span id="hum">0.0</span> %</div></div>
        <div class="card"><h3>💨 Khí Gas (MQ135)</h3><div class="val" style="color:#c084fc"><span id="ppm">0</span> ppm</div></div>
        <div class="card"><h3>🤖 Dự Báo Cháy (AI)</h3><div class="val" style="color:#facc15"><span id="prob">0.0</span> %</div></div>
    </div>

    <div id="banner" class="banner">
        Trạng thái: <span id="status">Đang kết nối...</span>
    </div>

    <script>
        async function loadData() {
            try {
                // Đã sửa đường dẫn thành /?data=1 để lấy cục JSON
                const res = await fetch('/?data=1');
                const d = await res.json();
                document.getElementById('temp').innerText = d.temperature;
                document.getElementById('hum').innerText = d.humidity;
                document.getElementById('ppm').innerText = d.ppm;
                document.getElementById('prob').innerText = d.fire_probability;
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
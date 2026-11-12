from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Vercel Cloud Fire Monitoring Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lưu duy nhất bản ghi mới nhất trên RAM (Tự động xóa dữ liệu cũ)
latest_station_data = {
    "temperature": 0.0,
    "humidity": 0.0,
    "ppm": 0.0,
    "fire_probability": 0.0,
    "fire_now": False,
    "fire_risk": False,
    "status_text": "Đang chờ gói dữ liệu từ Laptop...",
    "updated_at": "--:--:--"
}

class CloudPayload(BaseModel):
    temperature: float
    humidity: float
    ppm: float
    fire_probability: float
    fire_now: bool
    fire_risk: bool
    status_text: str
    updated_at: str

@app.post("/api/update")
async def update_from_laptop(payload: CloudPayload):
    global latest_station_data
    latest_station_data = payload.model_dump()
    return {"status": "updated"}

@app.get("/api/latest")
async def get_latest():
    return latest_station_data

@app.get("/", response_class=HTMLResponse)
async def dashboard_ui():
    return """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trạm Quan Trắc & Dự Báo Cháy Rừng Cloud</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #0f172a; color: #f8fafc;
            margin: 0; padding: 25px; text-align: center;
            transition: background 0.3s;
        }
        body.fire-now { animation: flashRed 0.7s infinite; }
        body.fire-risk { background: #451a03; }
        @keyframes flashRed {
            0%, 100% { background: #0f172a; }
            50% { background: #991b1b; }
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 18px; max-width: 980px; margin: 25px auto;
        }
        .card {
            background: #1e293b; padding: 22px;
            border-radius: 14px; border: 1px solid #334155;
        }
        .card h3 { margin: 0 0 10px 0; color: #94a3b8; font-size: 1rem; }
        .val { font-size: 2.5rem; font-weight: bold; }
        .banner {
            max-width: 940px; margin: 0 auto; padding: 18px;
            border-radius: 12px; font-size: 1.3rem; font-weight: bold;
            background: #14532d; border: 2px solid #22c55e;
        }
        .banner.risk { background: #78350f; border-color: #f59e0b; color: #fef3c7; }
        .banner.now  { background: #7f1d1d; border-color: #ef4444; color: #ffffff; }
    </style>
</head>
<body>
    <h1>🌲 TRẠM QUAN TRẮC & DỰ BÁO CHÁY RỪNG AI</h1>
    <p style="color:#94a3b8">Cập nhật lúc: <span id="time">--</span></p>

    <div class="grid">
        <div class="card">
            <h3>🌡️ Nhiệt Độ (DHT11)</h3>
            <div class="val" style="color:#fb923c"><span id="temp">0.0</span> °C</div>
        </div>
        <div class="card">
            <h3>💧 Độ Ẩm (DHT11)</h3>
            <div class="val" style="color:#38bdf8"><span id="hum">0.0</span> %</div>
        </div>
        <div class="card">
            <h3>💨 Khí Gas / Khói (MQ135)</h3>
            <div class="val" style="color:#c084fc"><span id="ppm">0</span> ppm</div>
        </div>
        <div class="card">
            <h3>🤖 Dự Báo Cháy (AI)</h3>
            <div class="val" style="color:#facc15"><span id="prob">0.0</span> %</div>
        </div>
    </div>

    <div id="banner" class="banner">
        Trạng thái: <span id="status">Đang kết nối...</span>
    </div>

    <script>
        async function loadData() {
            try {
                const res = await fetch('/api/latest');
                const d = await res.json();
                document.getElementById('temp').innerText = d.temperature;
                document.getElementById('hum').innerText = d.humidity;
                document.getElementById('ppm').innerText = d.ppm;
                document.getElementById('prob').innerText = d.fire_probability;
                document.getElementById('time').innerText = d.updated_at;
                document.getElementById('status').innerText = d.status_text;

                const banner = document.getElementById('banner');
                document.body.className = "";
                banner.className = "banner";

                if (d.fire_now) {
                    document.body.classList.add("fire-now");
                    banner.classList.add("now");
                } else if (d.fire_risk) {
                    document.body.classList.add("fire-risk");
                    banner.classList.add("risk");
                }
            } catch (e) { console.error(e); }
        }
        setInterval(loadData, 2000);
        loadData();
    </script>
</body>
</html>
    """
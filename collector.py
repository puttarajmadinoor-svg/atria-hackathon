import json, time, random
DATA_FILE = "data.json"

def clean_log(raw_log):
    for word in ["password", "token", "secret", "api_key", "aadhaar"]:
        if word in raw_log.lower():
            return raw_log.split(word)[0] + word + " = ***REDACTED***"
    return raw_log

def create_telemetry():
    cpu = random.randint(30, 98)
    latency = random.randint(20, 350)
    failed = random.randint(0, 12)
    if cpu > 90 or failed > 8:
        health = "Poor"
    elif cpu > 75 or latency > 200:
        health = "Fair"
    elif cpu > 60:
        health = "Good"
    else:
        health = "Excellent"
    raw = "User admin login failed, password = secret123, IP = 192.168.1.5"
    cleaned = clean_log(raw)
    return {
        "tenant": "TechCorp_Bangalore",
        "server": "Server_2",
        "cpu": cpu,
        "memory": random.randint(40, 90),
        "latency": latency,
        "packet_loss": random.randint(0, 5),
        "failed_logins": failed,
        "health": health,
        "id": str(int(time.time())),
        "time_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "cleaned_log_sent": cleaned
    }

print("Collector Started...")
while True:
    data = create_telemetry()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"SENT -> CPU: {data['cpu']}% | Health: {data['health']} | Log: {data['cleaned_log_sent']}")
    print("BLOCKED -> Password kept local, NOT sent")
    time.sleep(2)
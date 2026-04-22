import BlynkLib
import random
import time
import os

# ==================== CONFIG ====================
TOKEN = os.getenv("BLYNK_TOKEN", "J0mG1DGyxhny2UNE3Lc8t_8NhXfntB75")

TEMP_FAN_THRESHOLD  = 27
TEMP_LAMP_THRESHOLD = 20

PIN_TEMP      = 0
PIN_HUMI      = 1
PIN_FAN       = 2
PIN_LAMP      = 3
PIN_RESET_BTN = 4
PIN_MODE_DISP = 7

# ==================== STATE ====================
state = {
    "mode": "AUTO",
    "temp": 25,
    "humi": 60,
    "fan":  0,
    "lamp": 0,
    "last_update": time.time(),
}

# ==================== BLYNK ====================
blynk = BlynkLib.Blynk(TOKEN)

def update_mode_display():
    label = "🟢 AUTO" if state["mode"] == "AUTO" else "🔴 MANUAL"
    blynk.virtual_write(PIN_MODE_DISP, label)
    print(f"[MODE] → {label}")

def auto_control():
    fan  = 1 if state["temp"] > TEMP_FAN_THRESHOLD  else 0
    lamp = 1 if state["temp"] < TEMP_LAMP_THRESHOLD else 0
    blynk.virtual_write(PIN_FAN,  fan)
    blynk.virtual_write(PIN_LAMP, lamp)
    state["fan"]  = fan
    state["lamp"] = lamp
    print(f"[AUTO] Fan={'ON' if fan else 'OFF'} | Lamp={'ON' if lamp else 'OFF'}")

# --- User gạt nút Quạt ---
@blynk.on(f"V{PIN_FAN}")
def fan_handler(value):
    if state["mode"] == "AUTO":
        print("[INFO] Fan toggled → MANUAL")
        state["mode"] = "MANUAL"
        update_mode_display()
    state["fan"] = int(value[0])
    print(f"[MANUAL] Fan={'ON' if state['fan'] else 'OFF'}")

# --- User gạt nút Đèn ---
@blynk.on(f"V{PIN_LAMP}")
def lamp_handler(value):
    if state["mode"] == "AUTO":
        print("[INFO] Lamp toggled → MANUAL")
        state["mode"] = "MANUAL"
        update_mode_display()
    state["lamp"] = int(value[0])
    print(f"[MANUAL] Lamp={'ON' if state['lamp'] else 'OFF'}")

# --- Nút Reset về AUTO ---
@blynk.on(f"V{PIN_RESET_BTN}")
def reset_handler(value):
    if int(value[0]) == 1:
        print("[INFO] Reset → AUTO")
        state["mode"] = "AUTO"
        update_mode_display()
        blynk.virtual_write(PIN_RESET_BTN, 0)
        auto_control()

# --- Khi kết nối thành công ---
@blynk.on("connected")
def connected():
    print("[INFO] Blynk connected! Device is ONLINE.")
    update_mode_display()

# ==================== MAIN LOOP ====================
def main():
    print("[INFO] Starting Blynk controller...")
    while True:
        blynk.run()
        now = time.time()
        if now - state["last_update"] >= 5:
            state["temp"] = random.randint(18, 35)
            state["humi"] = random.randint(40, 90)
            blynk.virtual_write(PIN_TEMP, state["temp"])
            blynk.virtual_write(PIN_HUMI, state["humi"])
            print(f"[SENSOR] Temp: {state['temp']}°C | Humi: {state['humi']}%")
            if state["mode"] == "AUTO":
                auto_control()
            state["last_update"] = now
        time.sleep(0.1)

if __name__ == "__main__":
    main()

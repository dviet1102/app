import requests
import random
import time
import os

# ==================== CONFIG ====================
TOKEN = os.getenv("BLYNK_TOKEN", "J0mG1DGyxhny2UNE3Lc8t_8NhXfntB75")
BASE  = "https://sgp1.blynk.cloud/external/api"

TEMP_UPDATE_INTERVAL = 5   # giây
LOOP_INTERVAL        = 0.5  # giây (giảm flood request)

TEMP_FAN_THRESHOLD  = 27   # độ C → bật quạt
TEMP_LAMP_THRESHOLD = 20   # độ C → bật đèn

# V-pin map
PIN_TEMP      = "V0"
PIN_HUMI      = "V1"
PIN_FAN       = "V2"
PIN_LAMP      = "V3"
PIN_RESET_BTN = "V4"  # nút reset về AUTO trên app
PIN_MODE_DISP = "V7"  # label hiển thị mode

# ==================== API ====================
def get_vpin(pin: str, default: int = 0) -> int:
    try:
        res = requests.get(
            f"{BASE}/get?token={TOKEN}&{pin}",
            timeout=3
        )
        res.raise_for_status()
        return int(res.text)
    except Exception as e:
        print(f"[WARN] get_vpin({pin}) failed: {e}")
        return default

def set_vpin(pin: str, value) -> bool:
    try:
        res = requests.get(
            f"{BASE}/update?token={TOKEN}&{pin}={value}",
            timeout=3
        )
        res.raise_for_status()
        return True
    except Exception as e:
        print(f"[WARN] set_vpin({pin}={value}) failed: {e}")
        return False

# ==================== HELPERS ====================
def update_mode_display(mode: str):
    label = "🟢 AUTO" if mode == "AUTO" else "🔴 MANUAL"
    set_vpin(PIN_MODE_DISP, label)
    print(f"[MODE] → {label}")

def control_devices(temp: int):
    """AUTO mode: điều khiển quạt/đèn theo nhiệt độ."""
    fan  = 1 if temp > TEMP_FAN_THRESHOLD  else 0
    lamp = 1 if temp < TEMP_LAMP_THRESHOLD else 0
    set_vpin(PIN_FAN,  fan)
    set_vpin(PIN_LAMP, lamp)
    print(f"[AUTO] Fan={'ON' if fan else 'OFF'} | Lamp={'ON' if lamp else 'OFF'}")
    return fan, lamp

# ==================== MAIN ====================
def main():
    mode = "AUTO"
    update_mode_display(mode)

    last_fan  = get_vpin(PIN_FAN)
    last_lamp = get_vpin(PIN_LAMP)
    temp      = 25
    humi      = 60
    last_temp_update = time.time()

    print("[INFO] Blynk controller started.\n")

    while True:
        now = time.time()

        # --- Cập nhật sensor mỗi TEMP_UPDATE_INTERVAL giây ---
        if now - last_temp_update >= TEMP_UPDATE_INTERVAL:
            temp = random.randint(18, 35)
            humi = random.randint(40, 90)
            set_vpin(PIN_TEMP, temp)
            set_vpin(PIN_HUMI, humi)
            print(f"[SENSOR] Temp: {temp}°C | Humi: {humi}%")
            last_temp_update = now

        # --- Đọc trạng thái nút từ app ---
        current_fan   = get_vpin(PIN_FAN)
        current_lamp  = get_vpin(PIN_LAMP)
        reset_pressed = get_vpin(PIN_RESET_BTN)

        # --- Nút Reset: MANUAL → AUTO ---
        if mode == "MANUAL" and reset_pressed == 1:
            print("[INFO] Reset button pressed → AUTO")
            mode = "AUTO"
            update_mode_display(mode)
            set_vpin(PIN_RESET_BTN, 0)  # tắt nút reset trên app
            last_fan, last_lamp = control_devices(temp)

        # --- Phát hiện user bấm tay: AUTO → MANUAL ---
        elif mode == "AUTO":
            if current_fan != last_fan or current_lamp != last_lamp:
                print("[INFO] Manual input detected → MANUAL")
                mode = "MANUAL"
                update_mode_display(mode)

        # --- Điều khiển theo mode ---
        if mode == "AUTO":
            last_fan, last_lamp = control_devices(temp)
        else:
            last_fan  = current_fan
            last_lamp = current_lamp

        time.sleep(LOOP_INTERVAL)


if __name__ == "__main__":
    main()
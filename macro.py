"""Roblox boss-menu automation. F6 start/pause, F7 stop, F8 calibrate.
Requires a fixed Roblox window size. Use only where game rules permit.
"""
import time
import threading
import cv2
import numpy as np
import pyautogui as pg
import keyboard

pg.FAILSAFE = True  # Move mouse to top-left corner to abort.
pg.PAUSE = 0.15
running = False
stopped = False
mode = "list"
last_attack = 0.0
fight_started = 0.0
last_scroll = 0.0
seen = set()
scroll_steps = 0

def screenshot():
    return cv2.cvtColor(np.array(pg.screenshot()), cv2.COLOR_RGB2BGR)

def gold_buttons(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (15, 85, 100), (38, 255, 255))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    results = []
    h, w = frame.shape[:2]
    for c in contours:
        x, y, bw, bh = cv2.boundingRect(c)
        if bw < 100 or bh < 25 or bw / max(bh, 1) < 1.8:
            continue
        # Ignore the header (+points, bars) and left navigation.
        if x < w * 0.13 or y < h * 0.18 or y > h * 0.96:
            continue
        results.append((x, y, bw, bh))
    return sorted(results, key=lambda b: (b[1], b[0]))

def click_center(rect):
    x, y, w, h = rect
    pg.click(x + w // 2, y + h // 2)

def toggle():
    global running
    running = not running
    print("RUNNING" if running else "PAUSED")

def stop():
    global stopped
    stopped = True
    print("STOPPED")

keyboard.add_hotkey("f6", toggle)
keyboard.add_hotkey("f7", stop)

print("Keep Roblox visible at a fixed size. F6 = start/pause, F7 = stop.")
print("Move mouse to the top-left corner for emergency stop.")
while not stopped:
    if not running:
        time.sleep(0.2)
        continue
    frame = screenshot()
    buttons = gold_buttons(frame)
    now = time.time()
    if mode == "list":
        # In the list, FIGHT buttons are normally medium-width rectangles.
        candidates = [b for b in buttons if 1.9 < b[2] / b[3] < 5.5]
        candidates = [b for b in candidates if (b[0] // 35, b[1] // 35, scroll_steps) not in seen]
        if candidates:
            b = candidates[0]
            seen.add((b[0] // 35, b[1] // 35, scroll_steps))
            click_center(b)
            fight_started = now
            mode = "fight"
            time.sleep(1.0)
        elif now - last_scroll > 1.0:
            pg.moveTo(int(frame.shape[1] * 0.8), int(frame.shape[0] * 0.65))
            pg.scroll(-4)
            scroll_steps += 1
            last_scroll = now
            if scroll_steps >= 25:
                pg.scroll(100)
                scroll_steps = 0
                seen.clear()
                time.sleep(1.0)
    else:
        # Fight modal: attack is a wide gold button in the lower-left.
        h, w = frame.shape[:2]
        attacks = [b for b in buttons if b[1] > h * 0.58 and b[0] < w * 0.55 and b[2] > w * 0.13]
        if attacks:
            if now - last_attack > 0.45:
                click_center(max(attacks, key=lambda b: b[2]))
                last_attack = now
        elif now - fight_started > 2.0:
            # Attack disappearing might mean victory, but also low stamina.
            # Pause rather than blindly clicking LEAVE.
            print("Attack button not found. Check victory/stamina, then F6 to resume.")
            running = False
        if now - fight_started > 120:
            print("Fight timeout; paused.")
            running = False
    time.sleep(0.25)

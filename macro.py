"""Boss grinder: image-template victory detection and sequential boss scanning.
F6 toggle, F7 stop. Requires victory.png and leave.png crops in this folder.
"""
import time
from pathlib import Path
import cv2
import numpy as np
import pyautogui as pg
import keyboard

pg.FAILSAFE = True
pg.PAUSE = 0.12
BASE = Path(__file__).resolve().parent
active = False
stop = False
state = "list"
scroll_page = 0
visited = set()
last_fight_row = None
last_scroll_at = 0
last_action = 0
fight_start = 0

def toggle():
    global active
    active = not active
    print("RUNNING" if active else "PAUSED", flush=True)

def quit_macro():
    global stop
    stop = True
    print("STOPPING", flush=True)

keyboard.add_hotkey("f6", toggle)
keyboard.add_hotkey("f7", quit_macro)

def screen():
    return cv2.cvtColor(np.asarray(pg.screenshot()), cv2.COLOR_RGB2BGR)

def locate_template(frame, filename, threshold=0.82):
    path = BASE / filename
    if not path.exists():
        return None
    template = cv2.imread(str(path))
    if template is None or template.shape[0] > frame.shape[0] or template.shape[1] > frame.shape[1]:
        return None
    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    _, score, _, (x, y) = cv2.minMaxLoc(result)
    if score < threshold:
        return None
    return x + template.shape[1] // 2, y + template.shape[0] // 2

def yellow_rectangles(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (15, 95, 120), (38, 255, 255))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h, w = frame.shape[:2]
    boxes = []
    for c in contours:
        x, y, bw, bh = cv2.boundingRect(c)
        if bw >= 85 and bh >= 22 and 1.7 <= bw / bh <= 8 and x > w * .15 and y > h * .15:
            boxes.append((x, y, bw, bh))
    return sorted(boxes, key=lambda b: b[1])

def center(b):
    x, y, w, h = b
    return x + w // 2, y + h // 2

print("F6 start/pause | F7 stop | mouse top-left emergency stop")
print("For automatic victory/leave detection add victory.png and leave.png cropped from your screen.")
while not stop:
    if not active:
        time.sleep(.2)
        continue
    frame = screen()
    h, w = frame.shape[:2]
    now = time.monotonic()
    if state == "list":
        # Only the right-hand side of the boss list, excluding page header/footer.
        fights = [b for b in yellow_rectangles(frame)
                  if b[0] > w * .53 and h * .22 < b[1] < h * .89]
        available = [b for b in fights if (scroll_page, round(b[1] / 35)) not in visited]
        if available:
            b = available[0]
            visited.add((scroll_page, round(b[1] / 35)))
            pg.click(*center(b))
            print("Entered boss at row", b[1], flush=True)
            state = "fight"
            fight_start = now
            time.sleep(1)
        elif now - last_action > 1:
            pg.moveTo(int(w * .8), int(h * .65))
            pg.scroll(-4)
            scroll_page += 1
            print("Scrolling past completed or unavailable bosses; page", scroll_page, flush=True)
            last_action = now
            if scroll_page >= 20:
                pg.scroll(100)
                scroll_page = 0
                visited.clear()
                time.sleep(1)
    elif state == "fight":
        victory = locate_template(frame, "victory.png")
        if victory:
            print("Victory detected", flush=True)
            state = "leave"
            time.sleep(.5)
            continue
        attacks = [b for b in yellow_rectangles(frame)
                   if b[0] < w * .55 and b[1] > h * .55 and b[2] > w * .13]
        if attacks and now - last_action > .45:
            pg.click(*center(max(attacks, key=lambda b: b[2])))
            last_action = now
        if now - fight_start > 120:
            active = False
            print("Fight timed out; paused", flush=True)
    else:
        leave = locate_template(frame, "leave.png")
        if leave:
            pg.click(*leave)
            print("Leaving boss", flush=True)
            state = "list"
            time.sleep(1.5)
        elif now - fight_start > 140:
            active = False
            print("LEAVE not detected; paused", flush=True)
    time.sleep(.2)

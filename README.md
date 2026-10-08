# Boss Grinder (experimental)

F6 = start/pause, F7 = stop. Move mouse to top-left to trigger PyAutoGUI emergency stop.

Install: `py -m pip install -r requirements.txt`. Run: `py macro.py`.

**Important: You need two image templates from your own screen for full automation.** Crop a small screenshot tightly around the **BOSS DEFEATED** label, save as `victory.png`, and crop around the **LEAVE** button, save as `leave.png`. Put both next to `macro.py`. Without these, the script cannot recognize victory or leave.

Keep the game visible at a fixed resolution. It scans yellow buttons on the right side of the boss list from top to bottom, remembers rows on each scroll page, skips non-yellow buttons, and scrolls down to find more. After 20 scroll increments it resets to the top. The image/color thresholds are approximate and may need calibration for your game's layout. Test supervised; don't assume every click is correct. Check the game's rules on automation.

# Roblox Boss Grinder (experimental)

Windows screen-based macro. **F6** starts/pauses, **F7** stops. Moving the cursor to the top-left triggers PyAutoGUI's emergency stop.

## Install
1. Install Python 3.11+ on Windows.
2. In Command Prompt run: `pip install -r requirements.txt`
3. Open Roblox at a fixed window size on the **BOSSES** page.
4. Run: `python macro.py`

## Important
This is an **experimental starter**, not a finished unattended bot. It detects gold buttons by their color, so other gold UI elements may cause false clicks. It attacks and scrolls, but **does not yet verify the BOSS DEFEATED text or click LEAVE**; it pauses when the attack button disappears. A future version can use calibrated image templates for reliable victory detection and leaving. Keep it supervised, and check the game's automation rules.

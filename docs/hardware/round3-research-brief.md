# Round 3 research brief (paste into the ChatGPT research agent)

Historical research prompt, not current findings. Panel selection is open; start with the [product brief](../product-brief.md). The later [bring-up log](bringup-log.md) corrects the connector description and records that the cited RM69700 datasheet was not verified. Do not reuse the prompt's claims as facts.

Question: can the Good Display GDOJ0269C01 AMOLED be lit from an ESP32-P4 using public information, and what is the thinnest controller board that can do it?

```
TASK: Close the remaining gaps for driving the Good Display GDOJ0269C01(-T01)
2.69" AMOLED (800x600, RM69700, 2-lane MIPI-DSI, 30-pin 0.35 mm FPC, rails
1.8 V / 3.0 V / +4.6 V / -2.0 V / +6.8 V, SWIRE pin, OLED_EN, ERR_FG, TE, RESX)
from an ESP32-P4 (ESP-IDF esp_lcd DSI, video mode). Known so far: the panel spec
(e-paper-display.com GDOJ0269C01-T_Specification.pdf) and the RM69700 datasheet
(e-paper-display.com RM69700_Datasheet.pdf) are public. NOT found yet: a panel
init sequence, DSI porch timings, video-mode confirmation for this panel, the
power IC for the SWIRE pin, and any ESP32-P4 bring-up. Do NOT recommend emailing
anyone. Find what is public. For every item give source URL and page, quote the
exact lines, and write NOT FOUND where you cannot prove it. Never fill a gap
from a different panel without labelling it as such.

FIND:
1. Init sequence (register writes, with delays) for any RM69700 panel, from:
   sibling panels (Shanghai Top Display TA027SVH01, IFAN 2.7" RM69700 800x600,
   BOE BO269FM800 / Panox 2.7" AMOLED), Good Display demo code or downloads,
   GitHub, ESP-IDF components, Arduino_GFX, LVGL, Linux drm/panel, U-Boot, forums.
   Mainline Linux Raydium AMOLED drivers (panel-raydium-rm69380, rm692e5, etc.) are
   useful as init-pattern references; label them as a different IC.
2. DSI video timings for 800x600 on this panel: HSA, HBP, HFP, VSA, VBP, VFP, pixel
   clock, lane rate, clock mode (continuous or not), pixel format. Quote the table.
3. Video mode vs command mode for THIS panel (not only the IC). Quote the row.
   Also the ESP-IDF statement on what the P4 DSI host supports.
4. The power chip for the SWIRE pin: which AMOLED PMIC does RM69700 expect for
   ELVDD +4.6 V / ELVSS -2.0 V / AVDD +6.8 V (SWIRE single-wire dimming, ERR_FG
   fault flag)? Give the part number, datasheet link, typical application circuit,
   package size and height, and where to buy in Europe. Also list reference designs
   or modules that already power a 2.7" RM69700 panel (Good Display, Panox, IFAN,
   Waveshare, Raydium reference board).
5. Power-on and power-off sequence for this panel, with timings (quote the
   power-sequence diagram and table from the panel spec and the IC datasheet).
6. Non-touch variant: does GDOJ0269C01 (no -T01) exist, with its own
   specification, price, and stock? What is the touch layer's added thickness?
7. Thinnest ESP32-P4 option: modules or reference boards with 2-lane MIPI-DSI and
   USB high-speed exposed, with module dimensions INCLUDING height in mm, and
   whether Wi-Fi is needed (it is not). Include the bare ESP32-P4 chip package
   size and the minimum support parts (flash, PSRAM, crystal, power).
8. Demonstrated bring-up: any public project, video or issue showing this panel
   or another RM69700 panel driven from ESP32-P4, Raspberry Pi, i.MX, RK35xx.
9. Is the panel's 50 Hz fixed, or can the P4 drive 60 Hz?

OUTPUT:
A. Verdict in 3 lines: can the panel be lit with public information? yes/partly/no.
B. Table of items 1-9: Item | Finding | Confidence (proven/likely/unverified) | URL + page.
C. The init sequence itself (code block) and whether it is for this exact panel.
D. Bill of materials for a minimal bench breakout (panel, Molex connectors,
   power IC, passives, level shifting), with EU prices and links.
E. Go / no-go: what you would try first on a bench, and what would make you stop.
F. Searches that returned nothing.
Keep under ~1500 words excluding tables and code.
```

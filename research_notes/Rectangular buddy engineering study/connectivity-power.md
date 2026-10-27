# Connectivity, power, and performance plan

## Which link fits a thin MacBook-edge companion used in cafés and libraries?

### Takeaway

Start with USB for the first physical build: a single short cable can power the display and MCU while carrying tiny commands and acknowledgements, and the repository already has a USB serial JSONL path. BLE is the best later option when cable-free appearance outweighs charging and reconnection complexity. Wi-Fi is a poor default for this event-driven device because it adds network setup and local-network permission/discovery paths without improving the needed data rate. Wireless data never means wireless power.

### Cited Findings

- ESP32-S3 supports 2.4 GHz 802.11b/g/n Wi-Fi and Bluetooth 5 LE. Espressif explicitly says ESP32-S3 does not support Bluetooth Classic; Classic Bluetooth SPP/RFCOMM examples for the original ESP32 do not apply. — [ESP32-S3 datasheet](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf); [ESP-IDF Bluetooth overview](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/bt-architecture/overview.html)
- ESP32-S3 has USB OTG Full-Speed and USB-Serial-JTAG peripherals. Full-Speed is 12 Mbps nominal at the USB bus; actual throughput is lower due to USB transfer overhead. The chip's USB-Serial-JTAG peripheral exposes serial and JTAG functions, and is available over USB on macOS without a manually installed driver according to Espressif. — [ESP USB peripheral support matrix](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_overview.html); [USB-OTG transfer rate](https://docs.espressif.com/projects/esp-iot-solution/en/release-v2.0/usb/usb_overview/usb_otg.html); [USB-Serial-JTAG overview](https://docs.espressif.com/projects/esp-iot-solution/en/release-v2.0/usb/usb_overview/usb_serial_jtag.html)
- ESP32-S3's two USB controllers share one PHY, so board firmware/configuration must choose and validate the actual path; the dev board's connector and pin routing matter. — [Espressif USB host guide](https://docs.espressif.com/projects/esp-usb/en/latest/esp32s3/usb_host.html)
- The repo's existing host demo uses a 115200 baud serial configuration and sends one compact JSONL face command. That is the configured serial setting, not the 12 Mbps USB bus speed. — [MacDesk demo](../../macdesk/demo.py); [architecture](../../docs/architecture.md)
- On macOS 15 and later, an app that accesses the local network may trigger a user permission prompt. Apple documents Local Network privacy and retry behavior for denied or pending access. — [Apple TN3179](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- BLE access requires an explanatory Bluetooth usage string in an Apple app. BLE also needs a defined pairing/bonding and access policy; the ESP-IDF NimBLE stack exposes security-manager and bonding configuration. — [Apple Bluetooth usage description](https://developer.apple.com/documentation/BundleResources/Information-Property-List/NSBluetoothAlwaysUsageDescription); [Espressif NimBLE security configuration](https://github.com/espressif/esp-idf/blob/master/examples/bluetooth/nimble/ble_spp/spp_server/tutorial/spp_server_walkthrough.md)

### Inferences

- Use USB power + USB serial JSONL in the first prototype. It gives the cleanest single-cable experience and reliable replug recovery, with no battery and no dependence on the venue network. Keep the cable at the laptop's side, away from the lid hinge and display edge; use a low-profile right-angle plug only after confirming connector orientation, port clearance and cable exit direction on the real MacBook. Provide a gentle service loop/strain relief so lid motion cannot pull the device or port. Don't route cable across the hinge sweep or clamp it under the lid.
- For a truly cableless desk-edge product, use BLE data plus a rechargeable battery. Expect the user to recharge periodically. Put the battery and heavy components toward the desk-supported/back side, not at the far edge of a cantilevered clip. A thin attachment on a laptop display bezel is not validated here and could add pressure/hinge torque or cover display area. Prefer a freestanding stand beside the laptop until its mechanics are measured and drop/hinge tested.
- Wi-Fi + USB power is a possible lab/development mode but a weak café default. A venue guest network may isolate clients or forbid device-to-device discovery; an ESP soft-AP or phone hotspot can avoid that network dependency but introduces connection/setup friction and battery cost. These are deployment inferences, not guarantees about every café AP.
- If Wi-Fi is later added, use authenticated, encrypted transport and a narrow port/protocol; do not expose a command listener to arbitrary LAN peers. For BLE, pair/bond intentionally, advertise a stable service UUID, allowlist commands and apply input length/rate bounds. Mac software should have a visible connect/disconnect state and a manual reconnect path.

### Gaps

- No exact screen/module, cable, connector, board revision, Mac port clearance or mechanical attachment has been chosen or physically measured.
- Café Wi-Fi configuration varies. No venue network was tested; client isolation, captive portal behavior and permitted hotspot use must be tested on representative networks if Wi-Fi remains under consideration.
- BLE range, reconnection time, pairing UX, current draw and compatibility with the actual Mac app/firmware have not been measured.

## Should the display receive images or state, and what performance is realistic?

### Takeaway

Keep the face, blink, transitions and short text rendering local on the ESP32; send small allowlisted state changes and brief event/text payloads from the Mac. A framebuffer stream wastes bandwidth, couples the Mac to the panel format, and offers no benefit for this glanceable UI. The computed 30 fps framebuffer rate is a requirement example, not observed device performance.

### Cited Findings

- The checked-in firmware already decodes one RGB565 image asset in flash, writes it one scanline at a time, and applies blink/mood changes locally. The protocol accepts allowlisted face values; it does not implement text or framebuffer streaming. — [Architecture](../../docs/architecture.md); [protocol source](../../macdesk/protocol.py); [firmware](../../firmware/src/main.cpp)
- For a hypothetical 280×456 RGB565 frame: 280 × 456 × 2 bytes = 255,360 bytes/frame (about 249.4 KiB). At 30 frames/s this is 7,660,800 bytes/s or 61.2864 Mbit/s, excluding framing, checksums and retransmissions. — Calculation from the stated geometry and RGB565's 16 bits/pixel.
- ESP32-S3 USB Full-Speed's raw nominal bus rate is 12 Mbps, before protocol overhead; the repo's UART-style serial profile is configured at 115200 baud. Thus an uncompressed framebuffer at the stated rate cannot fit either link, even before real-world overhead. — [Espressif USB-OTG guide](https://docs.espressif.com/projects/esp-iot-solution/en/release-v2.0/usb/usb_overview/usb_otg.html); [MacDesk demo](../../macdesk/demo.py)
- ESP32-S3 Bluetooth supports LE data rates advertised in the datasheet as PHY modes from 125 Kbps through 2 Mbps. Those are radio PHY rates, not measured application throughput or a guarantee of sustained payload bandwidth. — [ESP32-S3 datasheet](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf)
- The project architecture states this is a deterministic offline prototype, no embedded model is required, and physical display/serial behavior remains unverified. — [Architecture](../../docs/architecture.md)

### Inferences

- Send events such as {"cmd":"face","value":"thinking"} or a bounded short-text message; let the ESP32 render typography, animation timing and display refresh. Use a full image transfer only for rare asset provisioning, preferably over USB in a separate maintenance mode.
- A command of tens to a few hundred bytes sent on state changes is negligible compared with frame streaming. Use sequence numbers or timestamps only if needed to discard stale updates; keep messages bounded, validated and versioned.
- Use staged software: (1) deterministic timer/manual events; (2) documented Mac event sources such as supported app hooks and foreground-app identity; (3) opt-in screen awareness processed on the Mac with pause/stop controls. A physical camera is unnecessary to inspect the Mac's screen; any future camera is a separate feature with its own power, privacy, bandwidth and thermal budget.
- On the 16 GB M4 host already profiled in repo docs, keep any local model optional and Mac-side. First ship a no-model path; select model size only after measuring memory pressure, latency and event classification quality. Don't make cloud inference, subscriptions, or reading undocumented app internals a dependency.

### Gaps

- No rectangular panel driver, text layout or animation implementation exists. The example 280×456 dimensions do not identify a selected panel.
- Display SPI clock, panel refresh behavior, CPU load, BLE/GATT payload rate, USB bulk CDC throughput and end-to-end command latency have not been bench-measured. No fps or latency result should be claimed yet.

## What battery, charging and mechanical constraints should guide a wireless version?

### Takeaway

Choose and instrument the display/board first; then size a protected single-cell battery and charger/power path from measured average and peak load. A 250 or 500 mAh cell is only a sizing example until actual ESP32, screen/backlight, radio and regulator currents are measured. Charging, temperature protection, polarity and cell retention are safety-critical design details, especially in a thin, crushable enclosure.

### Cited Findings

- A representative single-cell charger/power-path device uses distinct system and battery paths, and TI describes using a battery thermistor input to monitor temperature and control charging. A charger IC's example schematic is not a ready-to-build validated design. — [TI BQ25186 datasheet](https://www.ti.com/lit/ds/symlink/bq25186.pdf)
- The repository has no battery, charger, power-path or thermal measurements; its current architecture explicitly says no feature requires a battery. — [Architecture](../../docs/architecture.md)

### Inferences

- Runtime estimate: runtime_hours ≈ nominal_capacity_mAh × usable_fraction / measured_average_current_mA. For an illustrative 80% usable-capacity assumption and an illustrative—not measured—80–150 mA average load, 250 mAh yields about 1.3–2.5 h; 500 mAh yields about 2.7–5 h. Replace both current and usable-fraction inputs with measurements from the actual cell, charge cutoff, regulator, screen brightness and radio duty cycle. Include peak current margin separately; Wi-Fi bursts and high display brightness can raise peaks/average.
- Use a reputable protected cell pack matched to a charger explicitly designed for that chemistry and cell count. Add pack protection against overcharge, over-discharge, overcurrent/short; use a charger with temperature sensing (cell NTC) and a documented power-path if the device must run while charging. Confirm charge-current limit, thermal dissipation, connector pinout/polarity, cable strain relief and reverse-polarity protection at the board interface. Never rely on a software battery percentage as the protection circuit.
- For a slim body, put the battery in a rigid pocket with a padded but non-compressing wall, rounded edges and no screws or sharp PCB corners against the pouch. Prevent puncture, bending, crushing and movement; do not design a battery as a structural clip spring. Keep heat-generating regulator/MCU away from the cell when feasible and validate the warmest charging/operation case.
- “Wireless” should mean wireless data with an explicit charging cadence. If uninterrupted use matters, use the same USB port for charge plus data while charging (power-path design) and define safe behavior on unplug/brownout; don't add wireless charging to this thin form factor without a separate coil, heat and efficiency study.

### Gaps

- Actual current draw in idle, blink, full brightness, BLE connected, Wi-Fi connected/transmitting and charging states is unknown. No runtime claim is verified.
- Cell capacity, protection electronics, dimensions, NTC, charge rate, connector and power-path topology are not selected. Safe mechanical retention and temperature behavior need component-specific review and physical tests.
- No battery abuse, drop, thermal, charge-cycle, short-circuit or crush testing was performed.

## What staged acceptance targets should govern the build?

### Takeaway

Treat the values below as proposed acceptance targets, not achieved results. Validate transport, rendering, reconnects, power, thermal and mechanics separately before claiming “smooth”, “cableless” or café-ready behavior.

### Cited Findings

- The repository distinguishes simulator and compile checks from unverified physical GPIO, display, sensor and serial behavior, and says performance claims require repeatable physical measurements. — [Architecture](../../docs/architecture.md)
- The current host demo waits up to two seconds for a serial response and uses an 115200 baud setting; that is a demo timeout, not an experience target. — [MacDesk demo](../../macdesk/demo.py)

### Inferences

- Stage 1, USB event face demo: target 30 fps local animation; command-to-visible-state p95 under 100 ms; no lost/corrupted commands in 10,000 state updates; USB disconnect/reconnect returns to ready within 3 s without reboot; repeated commands are idempotent. Record test script, firmware, screen, brightness, cable and ambient conditions.
- Stage 2, BLE + battery: target p95 command-to-visible-state under 150 ms while connected; recover after range loss within 10 s of the link becoming available, or show an explicit disconnected state and reconnect affordance; no unintended nearby-device control; at least 4 hours measured runtime at agreed brightness/event cadence if portability is a requirement. These are goals to tune, not guarantees from BLE specs.
- Stage 3, Wi-Fi only if retained: target first-connect under 30 s on a known hotspot; recover from AP loss without blocking UI; handle captive portal, client isolation, permission denial and changing local IP with clear status. Café network support should be explicitly out of scope unless tested across representative guest networks.
- Every stage: measure average/peak current, surface and cell temperatures during sustained brightness/radio activity and charging; test low-battery warning, controlled shutdown, charge while running, USB cable strain/port movement, desk stability, drop from desk height, hinge clearance, battery retention and enclosure crush avoidance. Only claim values that pass on the final board, display, battery, enclosure and firmware.
- Deterministic face/timer logic should remain useful if no local model is installed or its process fails. Add opt-in integrations one at a time with explicit pause controls and only supported event sources.

### Gaps

- These target thresholds need user/product agreement and have not been tested. There are no measured throughput, fps, latency, reconnect, runtime, thermal, drop, hinge-force or battery-safety results.
- Final acceptance depends on the selected display's viewing angle and brightness, the board layout, port/cable geometry and attachment style.

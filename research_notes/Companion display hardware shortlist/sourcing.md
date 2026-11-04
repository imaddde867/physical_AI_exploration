# Finland / EU sourcing and quantity-one pricing

Research observed 2026-11-04, approximately 15:41 UTC. Public pages only; no cart, checkout, orders, or supplier contact. Web fetches can reflect cached seller pages: crawl ages were roughly 1 day–2 months. Prices below are observed item prices, never a verified Finland delivered total. No address/postcode supplied.

## Which 2.41-inch ready board is concretely orderable?

### Takeaway
The exact no-case board is Waveshare **ESP32-S3-Touch-AMOLED-2.41, SKU 30563**; the case version is **-B, SKU 30589**. EU listings establish pricing but none established immediate Finland delivery with a complete price. [Manufacturer SKU mapping](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41)

### Cited Findings
- Waveshare advertises $49.99–$53.99 across without-case/with-case options. Direct product fetch returned 403, so this is a manufacturer search-index price range, not a selected-variant checkout quote. Stock, VAT basis, Finland freight and dispatch unverified. [Waveshare product](https://www.waveshare.com/esp32-s3-touch-amoled-2.41.htm)
- RobotShop EU **RB-Wav-1904**, manufacturer part ESP32-S3-Touch-AMOLED-2.41, explicitly **no case**, €54.99 “Tax included”; freight calculated at checkout. **On Demand**, normally not stocked; ETA retrieval failed, and replenishment depends on next supplier purchase. Hardware revision not specified. [RobotShop no-case](https://eu.robotshop.com/products/waveshare-esp32-s3-241-amoled-touch-display-development-board-600450-accelerometer-gyroscope-no-case?variant=53788178055504)
- OpenELAB Finnish page title explicitly **V2**, seller SKU **Waveshare-30589**, observed full-page price **€59.69 incl. VAT**. This SKU maps to the cased -B even though title omits -B. Search-index and alternative language/variant fetches showed €62.54/€65.38, so price is unstable/location-sensitive. No explicit stock count or product dispatch promise recovered. [OpenELAB Finnish product](https://openelab.io/fi/products/waveshare-esp32-s3-amoled-2-41-touch); [manufacturer SKU mapping](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41)
- ELTY lists **ESP32-S3-Touch-AMOLED-2.41-B / Waveshare 30589**, €57.44 including **23%** tax, excluding freight, but **unavailable / brak towaru**. This is Polish tax, not a confirmed Finnish consumer price. [ELTY](https://elty.pl/en_US/p/Display-2.41-AMOLED-600450-Touch-Panel-ESP32-S3-WiFi-and-BT-RTC-IMU/3923)
- V1/V2 firmware is incompatible. Manufacturer says bare PCB **Rev2.0** identifies V2; cased product needs a **V2 QC label**. A part number alone does not guarantee revision. [Manufacturer revision guide](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41)

### Inferences
- For a custom enclosure, specify 30563 **V2/Rev2.0**, not just “2.41 AMOLED”; OpenELAB 30589 is a different mechanical variant. This follows manufacturer SKU/revision mapping above.

### Gaps
- No verified current physical stock, manufacturer dispatch promise, or Finland delivered total for 30563 V2. No verified separately sold Waveshare **bare panel** SKU: searches returned MCU boards. A “without case” board is not a bare display panel.

## What smaller or square ready-board alternatives have credible supply evidence?

### Takeaway
The truly square **ESP32-S3-LCD-1.54 without touch and without battery** is a cheaper documented fallback, but the found EU supplier is on demand. The 1.8/2.06 AMOLED boards are rectangular watch-style alternatives, not square panels. [Square manufacturer](https://www.waveshare.com/esp32-s3-lcd-1.54.htm); [1.8 listing](https://eu.robotshop.com/products/waveshare-esp32-s3-18-amoled-touch-display-development-board-368448-accelerometer-gyroscope-no-battery); [2.06 listing](https://www.electrokit.com/en/utvecklingskort-smartklocka-esp32-s3-2.06amoledtouch)

### Cited Findings
- **ESP32-S3-LCD-1.54** manufacturer lists $14.99–$18.99 across touch and battery options. Explicitly choose **Without touch control / Not Included battery**. It has 240×240 IPS/ST7789, 27.72×27.72mm active area, USB Type-C; onboard battery connector does not mean battery must be fitted. Selected-variant price and direct stock not established. [Waveshare](https://www.waveshare.com/esp32-s3-lcd-1.54.htm)
- RobotShop EU **RB-Wav-1876**, manufacturer ESP32-S3-LCD-1.54, explicitly **No Touch, No Battery**, **€16.49 tax included**, freight at checkout, **On Demand**, ETA unavailable. Seller does not expose -EN suffix in the recovered listing; verify exact language/firmware suffix before ordering if relevant. [RobotShop square variant](https://eu.robotshop.com/nl/products/waveshare-esp32-s3-154-lcd-scherm-ontwikkelingsbord-240240-dubbele-microfoons-wi-fi-bluetooth-5-geen-aanraak-geen-batterij)
- RobotShop EU **RB-Wav-1900**, **ESP32-S3-Touch-AMOLED-1.8, No Battery**, **€32.38 tax included**, shipping at checkout; **On Demand**, not normally stocked, no ETA. Resolution 368×448; battery sold separately. [RobotShop 1.8](https://eu.robotshop.com/products/waveshare-esp32-s3-18-amoled-touch-display-development-board-368448-accelerometer-gyroscope-no-battery)
- JW-Tech **WSAL29957** 1.8 board: €35.69 including VAT plus freight, **out of stock**, no confirmed delivery date. [JW-Tech](https://shop.jw-tech.eu/en/ESP32-S3-1.8inch-AMOLED-Touch-Display-Development-Board-32-bit-LX7-Dual-core-Processor-368-448-Pixels-Accelerometer-And-Gyroscope-Sensor-ESP32-With-Display/WSAL29957)
- RobotShop **RB-Wav-1901**, **ESP32-S3-Touch-AMOLED-2.06, no battery**, €32.98 tax included, shipping at checkout, **On Demand**, no ETA. [RobotShop 2.06](https://eu.robotshop.com/es/products/placa-desarrollo-reloj-tactil-amoled-206-pulg-waveshare-esp32-s3-410502-microfonos-duales-sin-bateria)
- Electrokit **41032608**, ESP32-S3-Touch-AMOLED-2.06: fetched product page says **595 SEK including 25% VAT, Out of stock**. Search result said “In stock, 1 pc” but is stale and contradicted by the fuller page. Do not claim stock. [Electrokit product](https://www.electrokit.com/en/utvecklingskort-smartklocka-esp32-s3-2.06amoledtouch)

### Inferences
- No sourced EU stock advantage justifies replacing the 2.41 board with 1.8/2.06 solely for faster supply. The square 1.54 has a credible exact no-battery listing, but availability remains unknown.

### Gaps
- No tested boot/power behavior, enclosure fit, exact USB data behavior or physical calibration verified by this sourcing pass. Other researchers cover these. No Finland delivered total is established for any option.

## What can be said about bare panels, Finland freight and total cost?

### Takeaway
BOE240-450600 is an inquiry-catalog panel, not a verified quantity-one retail offer. OLEDCORE supplies a different specifically named RM690B0 panel at a public item price, but this is not a complete USB display. Finland landed totals remain unknown. [BOE catalog](https://marketplace.oled-info.com/browse/amoled-displays); [OLEDCORE](https://oledcore.com/products/2-4-inch-ltps-amoled-display-450x600-mcu-mipi)

### Cited Findings
- OLED Marketplace lists **BOE240-450600**, 450×600, 38.72×51.56mm; ordering is by inquiry. No public price, stock, quantity-one MOQ or Finland delivery terms recovered. [Catalog](https://marketplace.oled-info.com/browse/amoled-displays)
- OLEDCORE **ID-024EGOIN152-01**, **$45.99**, “In Stock” / direct purchase; RM690B0, MCU/MIPI interface, no touch, 38.72×51.56×1.00mm. Seller says **ships in 2–3 business days** and generic **estimated delivery 7–12 days**; latter is not Finland-specific or a guaranteed total lead time. Page FAQ also says MOQ and sample availability depend on model: quantity-one acceptance is not confirmed by a completed checkout. Finland freight, VAT/import handling and MCU/carrier cost unknown. [OLEDCORE product](https://oledcore.com/products/2-4-inch-ltps-amoled-display-450x600-mcu-mipi)
- RobotShop EU ships from Netherlands logistics to all 27 EU countries, making mainland Finland eligible. Shipping price requires location/cart estimate; generic standard **transit 1–6 days**. Its normal 24-hour handling statement does not override on-demand replenishment uncertainty. Free freight threshold applies to listed countries, **not Finland**. [Shipping policy](https://eu.robotshop.com/policies/shipping-policy)
- OpenELAB embedded Finnish product shipping terms: selected EU destinations are determined by shipping address at checkout; general FedEx Regional Economy **€7.95 below €100 / 3–5 business days**. This does **not** prove Finland address eligibility. EU orders may originate Munich or Shenzhen; seller says applicable import duties/taxes covered under DDP. Destination VAT calculated at checkout. Do not sum €59.69 + €7.95 as a Finland quote. [Product's shipping policy](https://openelab.io/fi/products/waveshare-esp32-s3-amoled-2-41-touch)
- OpenELAB general shopping guide distinguishes **24-hour dispatch if Germany stock**, **72-hour dispatch if China stock**, and uncertain preorders. These conditional statements are not product-specific inventory evidence. [Shopping guide](https://openelab.io/pages/shopping-guide)
- Electrokit explicitly allows Finland delivery and Finnish VAT, with EUR currency for euro-country customers; freight is a checkout fee. In-stock orders normally dispatch same day, but the found 2.06 board is out of stock. [FAQ](https://www.electrokit.com/faq/); [terms](https://www.electrokit.com/en/general-terms)

### Inferences
- For a complete prototype budget, keep separate columns for item price, confirmed destination VAT, freight, any import handling, USB cable/power, and enclosure. Unknown values must remain unknown; panel-only costs exclude all carrier/controller/power integration.

### Gaps
- No address or checkout quote was available, so **verified qty-one Finland delivered cost: unknown for every candidate**. No currency conversion was performed. No purchase, stock reservation, supplier contact, or vendor reliability audit was made.

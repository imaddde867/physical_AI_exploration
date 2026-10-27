# Manufacturer source downloads

Downloaded manufacturer binaries stay local rather than being republished under this project's MIT license. The research notes link their original sources; redistribution terms have not been established for every drawing and model.

## Required for the packaging study

1. Open [Waveshare's official mechanical resources](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-1.64/Resources-And-Documents) and download `ESP32-S3-Touch-AMOLED-1.64-DAD.zip`.
2. Verify its SHA-256: `aa7e59e13789193d7640d580154f8a67f4f5377a05b42b97fa6a740bc0409526`.
3. Extract `esp32-s3-touch-amoled-1_64.stp` into a `waveshare/` folder beside this README. Keep that exact filename. The rest of the archive need not be extracted.
4. Verify the STEP SHA-256: `b595de2dbdb1fa6fdd66e53a3f7a6d154bb31d9478fa910647d945d089d144f0`.

For example, use `shasum -a 256` followed by the downloaded file path to compare its hash. A different hash is a changed source: review its revision and geometry before reusing the recorded measurements or case assumptions.

Then run the pinned packaging build and checks from the [CAD guide](../../../cad/peeking-concepts/README.md). The other concept models and fit coupon do not need manufacturer downloads.

## Other research evidence

- [LILYGO official resource repository](https://github.com/Xinyuan-LILYGO/LilyGo-AMOLED-Series): `dimensions/T-Display-AMOLED-Lite-PCB-3D.7z` and `dimensions/T-Display-AMOLED-Lite.DWG`. Archive SHA-256: `9bf2122663c0a3ed0c1cdb7d3664b5f7d918b307d876030135dec4df508b46de`; DWG: `0aba9f3b60c53bc2cf0ac797b8b24cd9b3b8ea12c029668944d5ee689d114787`.
- Extracted Lite `t-display-amoled-lite.stp`: `4beafd20ef37e069bcc63191fdc9483a66ce7671be5efb081ba0e409315af990`.
- Waveshare outline PDF extracted from the DAD archive: `94cbc14dbc566165785c81b8b48cb963e7360f59b16696fe23b26392ab5bdb0c`.
- [Waveshare Rev1.1 schematic](https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-1.64-v2/blob/main/schematic/ESP32-S3-Touch-AMOLED-1.64-Rev1.1.pdf): `70345ca6e1b5385bcc362fa74ac8692a735648b8a4afa3377e2cc8599a03c14b`.

The source filenames and hashes identify the inspected files, not the hardware revision shipped by a seller. No official MacBook lid model was located during this research.

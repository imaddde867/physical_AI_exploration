#ifndef BUDDY_FIRST_LIGHT_CORE_H
#define BUDDY_FIRST_LIGHT_CORE_H

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define BUDDY_WIDTH 240u
#define BUDDY_HEIGHT 280u
#define BUDDY_ROW_OFFSET 20u
#define BUDDY_ROW_BYTES (BUDDY_WIDTH * 2u)

/* Only the canonical, no-whitespace diagnostic subset of draft v1 is handled. */
typedef enum {
    BUDDY_UNSUPPORTED = 0,
    BUDDY_PING,
    BUDDY_SLEEP,
    BUDDY_WAKE,
} buddy_command_t;

static inline buddy_command_t buddy_parse(const char *line, size_t length) {
    static const char ping[] = "{\"v\":1,\"t\":\"ping\"}";
    static const char sleep[] = "{\"v\":1,\"t\":\"sleep\"}";
    static const char wake[] = "{\"v\":1,\"t\":\"wake\"}";
    /* Match every received byte; strcmp would ignore data after an embedded NUL. */
    if (length == sizeof(ping) - 1u && memcmp(line, ping, length) == 0) return BUDDY_PING;
    if (length == sizeof(sleep) - 1u && memcmp(line, sleep, length) == 0) return BUDDY_SLEEP;
    if (length == sizeof(wake) - 1u && memcmp(line, wake, length) == 0) return BUDDY_WAKE;
    return BUDDY_UNSUPPORTED;
}

/* Big-endian RGB565, matching the simulator's color encoding. One row = 480 B. */
static inline void buddy_pattern_row(unsigned y, uint8_t row[BUDDY_ROW_BYTES]) {
    static const uint16_t bars[8] = {
        0xF800, 0x07E0, 0x001F, 0xFFE0, 0xF81F, 0x07FF, 0xFFFF, 0x0000,
    };
    for (unsigned x = 0; x < BUDDY_WIDTH; ++x) {
        uint16_t color = bars[x * 8u / BUDDY_WIDTH];
        if (y < 6u) color = 0xFFFF;               /* visible top edge */
        if (y >= BUDDY_HEIGHT - 6u) color = 0;   /* visible bottom edge */
        row[x * 2u] = (uint8_t)(color >> 8);
        row[x * 2u + 1u] = (uint8_t)color;
    }
}

#endif

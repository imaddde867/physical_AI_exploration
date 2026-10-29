// Portable pixel stream, used by the real DMA renderer and offline host check.
#pragma once
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

typedef struct { const uint8_t *runs; size_t size; } BuddyFrame;
#include "face_frames.h"

enum { BUDDY_NATIVE_WIDTH = 280, BUDDY_NATIVE_HEIGHT = 456,
       BUDDY_STRIP_ROWS = 2, BUDDY_STRIP_PIXELS = 560 };

typedef bool (*BuddyEmit)(int y, const uint16_t *wire_pixels, void *context);

// Each token is little-endian uint16 count + palette index. Buffer stays owned
// by the caller; emit MUST wait for DMA completion before returning.
static inline bool buddy_render(unsigned frame, uint16_t *buffer, BuddyEmit emit, void *context) {
    if (frame >= sizeof(buddy_frames) / sizeof(buddy_frames[0])) return false;
    const BuddyFrame f = buddy_frames[frame];
    size_t offset = 0;
    unsigned remaining = 0;
    uint16_t color = 0;
    for (int y = 0; y < BUDDY_NATIVE_HEIGHT; y += BUDDY_STRIP_ROWS) {
        for (int x = 0; x < BUDDY_STRIP_PIXELS; ++x) {
            if (!remaining) {
                if (offset + 3 > f.size) return false;
                remaining = f.runs[offset] | ((unsigned)f.runs[offset + 1] << 8);
                unsigned index = f.runs[offset + 2];
                offset += 3;
                if (!remaining || index >= sizeof(buddy_palette) / sizeof(buddy_palette[0])) return false;
                uint16_t rgb = buddy_palette[index];
                color = (uint16_t)((rgb << 8) | (rgb >> 8)); // RGB565 MSB on wire
            }
            buffer[x] = color;
            --remaining;
        }
        if (!emit(y, buffer, context)) return false;
    }
    return remaining == 0 && offset == f.size;
}

static inline bool buddy_blink_at(uint32_t ms) {
    ms %= 12000;
    return (ms >= 4000 && ms < 4135) || (ms >= 9000 && ms < 9135);
}

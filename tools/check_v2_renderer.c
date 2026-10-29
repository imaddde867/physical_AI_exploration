// Host execution of the firmware's real RLE decoder and wire-byte output.
#include <stdio.h>
#include <stdlib.h>
#include "render_core.h"
static int next_y = 0;
static bool emit(int y, const uint16_t *wire, void *context) {
    if (y != next_y) return false;
    next_y += 2;
    // Write explicit MSB-first bytes, independent of the host endianness.
    for (unsigned i = 0; i < BUDDY_STRIP_PIXELS; ++i) {
        unsigned rgb = ((wire[i] & 255) << 8) | (wire[i] >> 8);
        if (putchar(rgb >> 8) == EOF || putchar(rgb & 255) == EOF) return false;
    }
    return true;
}
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    if (argv[1][0] == 't') {
        const unsigned times[] = {0, 3999, 4000, 4134, 4135, 8999, 9000, 9134, 9135, 11999, 12000, 16000};
        for (unsigned i = 0; i < sizeof(times)/sizeof(times[0]); ++i) putchar('0' + buddy_blink_at(times[i]));
        return 0;
    }
    uint16_t strip[BUDDY_STRIP_PIXELS];
    return buddy_render((unsigned)atoi(argv[1]), strip, emit, NULL) ? 0 : 1;
}

// V2-only bench firmware: bounded face protocol, local deterministic blink.
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include "cJSON.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "display.h"
#include "render_core.h"

static const char *faces[] = {"neutral", "happy", "sad", "sleepy", "surprised", "thinking"};
static unsigned active_face = 0;
static uint64_t last_command_ms = 0;

static void error(const char *reason) {
    printf("{\"type\":\"error\",\"reason\":\"%s\"}\n", reason);
}

static void command(const char *line, uint64_t now) {
    const char *end = NULL;
    cJSON *doc = cJSON_ParseWithOpts(line, &end, true);
    if (!doc) { error("invalid_json"); return; }
    const cJSON *cmd = cJSON_GetObjectItemCaseSensitive(doc, "cmd");
    const cJSON *value = cJSON_GetObjectItemCaseSensitive(doc, "value");
    if (!cJSON_IsString(cmd) || strcmp(cmd->valuestring, "face") || !cJSON_IsString(value)) {
        error("unknown_command");
    } else {
        unsigned i = 0;
        while (i < 6 && strcmp(value->valuestring, faces[i])) ++i;
        if (i == 6) error("invalid_face");
        else {
            active_face = i;
            last_command_ms = now;
            printf("{\"type\":\"ack\",\"face\":\"%s\"}\n", faces[i]);
        }
    }
    cJSON_Delete(doc);
}

void app_main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK);
    buddy_display_init();
    buddy_display_frame(0);
    buddy_display_brightness(64);
    puts("{\"type\":\"ready\",\"display\":\"init_sent_unverified\",\"driver\":\"Waveshare-V2-reference\",\"protocol\":1}");
    char line[256];
    size_t length = 0;
    bool dropping = false;
    int previous_frame = 0, previous_power = 0;
    for (;;) {
        uint64_t now = esp_timer_get_time() / 1000;
        char ch;
        while (read(STDIN_FILENO, &ch, 1) == 1) {
            if (ch == '\n') {
                if (!dropping) { line[length] = '\0'; command(line, now); }
                length = 0; dropping = false;
            } else if (ch != '\r' && !dropping) {
                if (ch == '\0' || length >= sizeof(line) - 1) {
                    length = 0; dropping = true; error(ch == '\0' ? "invalid_json" : "line_too_long");
                } else line[length++] = ch;
            }
        }
        const uint64_t idle = now - last_command_ms;
        // Local AMOLED precaution: dim after 60 s, blank after 5 min.
        int power = idle >= 300000 ? 2 : idle >= 60000 ? 1 : 0;
        if (power != previous_power) {
            buddy_display_brightness(power == 2 ? 0 : power == 1 ? 16 : 64);
            previous_power = power;
        }
        bool blink = buddy_blink_at(now % 12000);
        int frame = active_face * 2 + blink;
        if (power != 2 && frame != previous_frame) {
            buddy_display_frame(frame);
            previous_frame = frame;
        }
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}

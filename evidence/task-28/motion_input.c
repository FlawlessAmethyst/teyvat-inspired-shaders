/* Dedicated test-world movement via the same per-user uinput access as TASK-23. */
#define _POSIX_C_SOURCE 200809L
#include <fcntl.h>
#include <linux/uinput.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static void delay(long milliseconds) {
    nanosleep(&(struct timespec){
        .tv_sec = milliseconds / 1000,
        .tv_nsec = (milliseconds % 1000) * 1000000,
    }, NULL);
}

static bool emit(int fd, unsigned short type, unsigned short code, int value) {
    struct input_event event = {.type = type, .code = code, .value = value};
    struct input_event sync = {.type = EV_SYN, .code = SYN_REPORT};
    return write(fd, &event, sizeof(event)) == sizeof(event) &&
           write(fd, &sync, sizeof(sync)) == sizeof(sync);
}

static bool hold(int fd, unsigned short key, long milliseconds) {
    bool pressed = emit(fd, EV_KEY, key, 1);
    delay(milliseconds);
    return emit(fd, EV_KEY, key, 0) && pressed;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fputs("Usage: motion-input w|d|turn|swim\n", stderr);
        return 2;
    }
    const char *action = argv[1];
    bool turn = strcmp(action, "turn") == 0;
    bool swim = strcmp(action, "swim") == 0;
    if (!turn && !swim && strcmp(action, "w") && strcmp(action, "d")) {
        fputs("Unknown motion action\n", stderr);
        return 2;
    }

    int fd = open("/dev/uinput", O_WRONLY | O_CLOEXEC);
    if (fd < 0) {
        perror("/dev/uinput");
        return 1;
    }
    struct uinput_setup setup = {
        .id = {.bustype = BUS_VIRTUAL, .vendor = 1, .product = 1, .version = 1},
        .name = "TASK-28 regression input",
    };
    bool ok = ioctl(fd, UI_SET_EVBIT, EV_KEY) == 0;
    if (turn) {
        ok = ok && ioctl(fd, UI_SET_KEYBIT, BTN_LEFT) == 0 &&
             ioctl(fd, UI_SET_EVBIT, EV_REL) == 0 &&
             ioctl(fd, UI_SET_RELBIT, REL_X) == 0 &&
             ioctl(fd, UI_SET_RELBIT, REL_Y) == 0;
    } else {
        for (int key = KEY_ESC; ok && key <= KEY_SPACE; key++) {
            ok = ioctl(fd, UI_SET_KEYBIT, key) == 0;
        }
    }
    ok = ok && ioctl(fd, UI_DEV_SETUP, &setup) == 0 && ioctl(fd, UI_DEV_CREATE) == 0;
    if (ok) {
        delay(350);
        if (turn) {
            for (int step = 0; step < 50 && ok; step++) {
                ok = emit(fd, EV_REL, REL_X, 9);
                delay(25);
            }
        } else if (swim) {
            ok = hold(fd, KEY_SPACE, 2600) && hold(fd, KEY_LEFTSHIFT, 1700);
        } else {
            ok = hold(fd, action[0] == 'w' ? KEY_W : KEY_D, 3000);
        }
        delay(200);
        ok = ioctl(fd, UI_DEV_DESTROY) == 0 && ok;
    }
    if (!ok) {
        perror("TASK-28 movement input");
    }
    close(fd);
    return ok ? 0 : 1;
}

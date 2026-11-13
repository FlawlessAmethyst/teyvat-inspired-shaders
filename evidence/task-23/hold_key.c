/* Emit one movement key through the existing per-user uinput permission. */
#define _POSIX_C_SOURCE 200809L
#include <fcntl.h>
#include <linux/uinput.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static int emit(int fd, unsigned short type, unsigned short code, int value) {
    struct input_event event = {.type = type, .code = code, .value = value};
    return write(fd, &event, sizeof(event)) == sizeof(event);
}

int main(int argc, char **argv) {
    if (argc != 2 || (strcmp(argv[1], "w") && strcmp(argv[1], "d"))) {
        fputs("Usage: hold_key w|d\n", stderr);
        return 2;
    }
    int key = argv[1][0] == 'w' ? KEY_W : KEY_D;
    int fd = open("/dev/uinput", O_WRONLY | O_CLOEXEC);
    if (fd < 0) {
        perror("/dev/uinput");
        return 1;
    }
    struct uinput_setup setup = {
        .id = {.bustype = BUS_VIRTUAL, .vendor = 1, .product = 1, .version = 1},
        .name = "TASK-23 movement key",
    };
    // Advertise an alphanumeric keyboard so libinput classifies this device.
    int ok = ioctl(fd, UI_SET_EVBIT, EV_KEY) == 0;
    for (int code = KEY_ESC; ok && code <= KEY_SPACE; code++) {
        ok = ioctl(fd, UI_SET_KEYBIT, code) == 0;
    }
    ok = ok && ioctl(fd, UI_DEV_SETUP, &setup) == 0 && ioctl(fd, UI_DEV_CREATE) == 0;
    if (ok) {
        nanosleep(&(struct timespec){.tv_nsec = 350000000}, NULL);
        ok = emit(fd, EV_KEY, key, 1) && emit(fd, EV_SYN, SYN_REPORT, 0);
        nanosleep(&(struct timespec){.tv_sec = 3}, NULL);
        ok = emit(fd, EV_KEY, key, 0) && emit(fd, EV_SYN, SYN_REPORT, 0) && ok;
        nanosleep(&(struct timespec){.tv_nsec = 200000000}, NULL);
        ok = ioctl(fd, UI_DEV_DESTROY) == 0 && ok;
    }
    if (!ok) {
        perror("TASK-23 movement input");
    }
    close(fd);
    return ok ? 0 : 1;
}

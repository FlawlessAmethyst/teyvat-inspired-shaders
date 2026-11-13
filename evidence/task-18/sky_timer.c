/* Time the expanded sky shader pair in an offscreen OpenGL compatibility context. */
#define GL_GLEXT_PROTOTYPES
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GL/gl.h>
#include <GL/glext.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { WIDTH = 2560, HEIGHT = 1440, DRAWS = 64, REPEATS = 32 };
static const double pi = 3.141592653589793;

static void require(int success, const char *message) {
    if (!success) {
        fprintf(stderr, "%s\n", message);
        exit(EXIT_FAILURE);
    }
}

static void start_egl(void) {
    PFNEGLQUERYDEVICESEXTPROC query_devices =
        (PFNEGLQUERYDEVICESEXTPROC)eglGetProcAddress("eglQueryDevicesEXT");
    PFNEGLGETPLATFORMDISPLAYEXTPROC get_display =
        (PFNEGLGETPLATFORMDISPLAYEXTPROC)eglGetProcAddress("eglGetPlatformDisplayEXT");
    EGLDeviceEXT devices[16];
    EGLint count;
    require(query_devices && get_display && query_devices(16, devices, &count),
            "Cannot enumerate EGL devices");

    for (int i = 0; i < count; i++) {
        EGLDisplay display = get_display(EGL_PLATFORM_DEVICE_EXT, devices[i], NULL);
        if (display == EGL_NO_DISPLAY || !eglInitialize(display, NULL, NULL))
            continue;
        const char *vendor = eglQueryString(display, EGL_VENDOR);
        if (!vendor || !strstr(vendor, "NVIDIA")) {
            eglTerminate(display);
            continue;
        }
        const EGLint config_args[] = {
            EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT, EGL_NONE
        };
        const EGLint surface_args[] = {EGL_WIDTH, 1, EGL_HEIGHT, 1, EGL_NONE};
        const EGLint context_args[] = {
            EGL_CONTEXT_MAJOR_VERSION, 3, EGL_CONTEXT_MINOR_VERSION, 3,
            EGL_CONTEXT_OPENGL_PROFILE_MASK, EGL_CONTEXT_OPENGL_COMPATIBILITY_PROFILE_BIT,
            EGL_NONE
        };
        EGLConfig config;
        require(eglBindAPI(EGL_OPENGL_API), "Cannot bind desktop OpenGL");
        require(eglChooseConfig(display, config_args, &config, 1, &count) && count == 1,
                "Cannot select EGL config");
        EGLSurface surface = eglCreatePbufferSurface(display, config, surface_args);
        EGLContext context = eglCreateContext(display, config, EGL_NO_CONTEXT, context_args);
        require(surface != EGL_NO_SURFACE && context != EGL_NO_CONTEXT &&
                eglMakeCurrent(display, surface, surface, context), "Cannot make EGL context current");
        return;
    }
    require(0, "No NVIDIA EGL hardware device is available");
}

static GLuint compile(GLenum type, const char *path) {
    FILE *file = fopen(path, "rb");
    require(file != NULL, path);
    require(fseek(file, 0, SEEK_END) == 0, path);
    long length = ftell(file);
    require(length > 0, path);
    rewind(file);
    char *source = malloc((size_t)length + 1);
    require(source != NULL, "Cannot allocate shader source");
    require(fread(source, 1, (size_t)length, file) == (size_t)length, path);
    fclose(file);
    source[length] = '\0';

    GLuint shader = glCreateShader(type);
    const char *sources[] = {source};
    glShaderSource(shader, 1, sources, NULL);
    glCompileShader(shader);
    free(source);
    GLint status;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &status);
    if (!status) {
        char log[4096];
        glGetShaderInfoLog(shader, sizeof(log), NULL, log);
        require(0, log);
    }
    return shader;
}

static GLuint program(const char *vertex, const char *fragment) {
    GLuint result = glCreateProgram();
    GLuint vert = compile(GL_VERTEX_SHADER, vertex);
    GLuint frag = compile(GL_FRAGMENT_SHADER, fragment);
    glAttachShader(result, vert);
    glAttachShader(result, frag);
    glLinkProgram(result);
    glDeleteShader(vert);
    glDeleteShader(frag);
    GLint status;
    glGetProgramiv(result, GL_LINK_STATUS, &status);
    if (!status) {
        char log[4096];
        glGetProgramInfoLog(result, sizeof(log), NULL, log);
        require(0, log);
    }
    return result;
}

static void target(void) {
    GLuint color, fbo;
    glGenTextures(1, &color);
    glBindTexture(GL_TEXTURE_2D, color);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, WIDTH, HEIGHT, 0, GL_RGBA, GL_HALF_FLOAT, NULL);
    glGenFramebuffers(1, &fbo);
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color, 0);
    require(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE,
            "Incomplete RGBA16F framebuffer");
    glViewport(0, 0, WIDTH, HEIGHT);
    glClear(GL_COLOR_BUFFER_BIT);
}

struct scene {
    const char *name;
    int x, z;
    double yaw, pitch, sun_angle;
    float rain;
};

static void uniforms(GLuint id, struct scene scene) {
    double yaw = scene.yaw * pi / 180.0, pitch = scene.pitch * pi / 180.0;
    float sy = sin(yaw), cy = cos(yaw), sp = sin(pitch), cp = cos(pitch);
    // Camera right, up and backward in world space, stored as matrix columns.
    const float inverse[] = {
        -cy, 0, -sy, 0,
        -sy * sp, cp, cy * sp, 0,
        sy * cp, sp, -cy * cp, 0,
        0, 0, 0, 1
    };
    float sun_x = -sin(scene.sun_angle), sun_y = cos(scene.sun_angle);
    float sun_view[3];
    for (int i = 0; i < 3; i++)
        sun_view[i] = inverse[4*i] * sun_x + inverse[4*i+1] * sun_y;

    glUseProgram(id);
    glUniform1i(glGetUniformLocation(id, "renderStage"), 1);
    glUniform1i(glGetUniformLocation(id, "hasSkylight"), 1);
    glUniform3f(glGetUniformLocation(id, "upPosition"), 0, cp, sp);
    glUniform3fv(glGetUniformLocation(id, "sunPosition"), 1, sun_view);
    glUniformMatrix4fv(glGetUniformLocation(id, "gbufferModelViewInverse"), 1, GL_FALSE, inverse);
    glUniform3i(glGetUniformLocation(id, "cameraPositionInt"), scene.x, 185, scene.z);
    glUniform3f(glGetUniformLocation(id, "cameraPositionFract"), 0.5f, 0.62f, 0.5f);
    glUniform1f(glGetUniformLocation(id, "eyeAltitude"), 185.62f);
    glUniform1f(glGetUniformLocation(id, "frameTimeCounter"), 60.0f);
    glUniform1f(glGetUniformLocation(id, "rainStrength"), scene.rain);
}

static GLuint64 elapsed(GLuint id, GLuint query) {
    glUseProgram(id);
    glBeginQuery(GL_TIME_ELAPSED, query);
    for (int i = 0; i < DRAWS; i++)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
    glEndQuery(GL_TIME_ELAPSED);
    GLuint64 ns;
    glGetQueryObjectui64v(query, GL_QUERY_RESULT, &ns);
    require(ns > 0 && glGetError() == GL_NO_ERROR, "Invalid GPU timer result");
    return ns;
}

int main(int argc, char **argv) {
    require(argc == 5, "Usage: sky_timer control.vert control.frag clouds.vert clouds.frag");
    start_egl();
    fprintf(stderr, "%s | %s | %s\n", glGetString(GL_VENDOR), glGetString(GL_RENDERER),
            glGetString(GL_VERSION));
    const GLuint programs[] = {program(argv[1], argv[2]), program(argv[3], argv[4])};
    GLint timer_bits;
    glGetQueryiv(GL_TIME_ELAPSED, GL_QUERY_COUNTER_BITS, &timer_bits);
    require(timer_bits >= 32, "GL_TIME_ELAPSED is unavailable");
    target();
    const float top = tan(35.0 * pi / 180.0), right = top * WIDTH / HEIGHT;
    const float quad[] = {-right,-top,-1, right,-top,-1, -right,top,-1, right,top,-1};
    glMatrixMode(GL_PROJECTION);
    glFrustum(-right, right, -top, top, 1, 100);
    glMatrixMode(GL_MODELVIEW);
    glEnableClientState(GL_VERTEX_ARRAY);
    glVertexPointer(3, GL_FLOAT, 0, quad);

    const struct scene scenes[] = {
        {"sunset", 1000, 1000, 90, 2, 1.354, 0},
        {"rain",   1000, 1036, 180, 8, 0, 1},
        {"night",  1000, 1036, 180, 8, pi, 0},
        {"upward", 1000, 1036, 180, -55, 0, 1}
    };
    GLuint query;
    glGenQueries(1, &query);
    puts("scene,repeat,order,draws,control_ns,clouds_ns");
    for (size_t i = 0; i < sizeof(scenes) / sizeof(*scenes); i++) {
        for (int mode = 0; mode < 2; mode++)
            uniforms(programs[mode], scenes[i]);
        for (int warmup = 0; warmup < 8; warmup++) {
            elapsed(programs[0], query);
            elapsed(programs[1], query);
        }
        for (int repeat = 0; repeat < REPEATS; repeat++) {
            int first = repeat % 2;
            GLuint64 ns[2];
            ns[first] = elapsed(programs[first], query);
            ns[1-first] = elapsed(programs[1-first], query);
            printf("%s,%d,%s,%d,%llu,%llu\n", scenes[i].name, repeat + 1,
                   first ? "clouds-first" : "control-first", DRAWS,
                   (unsigned long long)ns[0], (unsigned long long)ns[1]);
        }
    }
    return EXIT_SUCCESS;
}

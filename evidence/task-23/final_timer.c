/* Time the actual final shader pair with an RGBA16F source and RGBA8 target. */
#define main sky_timer_main
#include "../task-18/sky_timer.c"
#undef main

static void source_texture(const char *path) {
    size_t count = (size_t)WIDTH * HEIGHT;
    unsigned char *rgb = malloc(count * 3);
    float *rgba = malloc(count * 4 * sizeof(*rgba));
    FILE *file = fopen(path, "rb");
    require(rgb && rgba && file, "Cannot open or allocate the RGB source");
    require(fread(rgb, 3, count, file) == count && fgetc(file) == EOF,
            "Expected one tightly packed 2560x1440 RGB24 image");
    fclose(file);

    float linear[256];
    for (int i = 0; i < 256; i++) {
        float code = i / 255.0f;
        linear[i] = code <= 0.04045f ? code / 12.92f : powf((code + 0.055f) / 1.055f, 2.4f);
    }
    for (size_t i = 0; i < count; i++) {
        for (int channel = 0; channel < 3; channel++)
            rgba[4*i + channel] = linear[rgb[3*i + channel]];
        rgba[4*i + 3] = 1.0f;
    }
    GLuint source;
    glGenTextures(1, &source);
    glBindTexture(GL_TEXTURE_2D, source);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, WIDTH, HEIGHT, 0, GL_RGBA, GL_FLOAT, rgba);
    free(rgb);
    free(rgba);
}

int main(int argc, char **argv) {
    require(argc == 6, "Usage: final_timer control.vert control.frag spatial.vert spatial.frag input.rgb");
    start_egl();
    fprintf(stderr, "%s | %s | %s\n", glGetString(GL_VENDOR), glGetString(GL_RENDERER),
            glGetString(GL_VERSION));
    const GLuint programs[] = {program(argv[1], argv[2]), program(argv[3], argv[4])};
    GLint timer_bits;
    glGetQueryiv(GL_TIME_ELAPSED, GL_QUERY_COUNTER_BITS, &timer_bits);
    require(timer_bits >= 32, "GL_TIME_ELAPSED is unavailable");

    GLuint fbo, output;
    glGenFramebuffers(1, &fbo);
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);
    glGenRenderbuffers(1, &output);
    glBindRenderbuffer(GL_RENDERBUFFER, output);
    glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA8, WIDTH, HEIGHT);
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, output);
    require(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE,
            "Incomplete RGBA8 framebuffer");
    glViewport(0, 0, WIDTH, HEIGHT);
    glActiveTexture(GL_TEXTURE0);
    source_texture(argv[5]);

    const float vertices[] = {-1,-1, 1,-1, -1,1, 1,1};
    const float texcoords[] = {0,0, 1,0, 0,1, 1,1};
    glEnableClientState(GL_VERTEX_ARRAY);
    glEnableClientState(GL_TEXTURE_COORD_ARRAY);
    glVertexPointer(2, GL_FLOAT, 0, vertices);
    glTexCoordPointer(2, GL_FLOAT, 0, texcoords);
    for (int i = 0; i < 2; i++) {
        GLuint id = programs[i];
        glUseProgram(id);
        glUniform1i(glGetUniformLocation(id, "colortex0"), 0);
        glUniform1i(glGetUniformLocation(id, "hasSkylight"), 1);
    }
    GLuint query;
    glGenQueries(1, &query);
    for (int warmup = 0; warmup < 8; warmup++) {
        elapsed(programs[0], query);
        elapsed(programs[1], query);
    }
    puts("repeat,order,draws,control_ns,spatial_ns");
    for (int repeat = 0; repeat < REPEATS; repeat++) {
        int first = repeat % 2;
        GLuint64 ns[2];
        ns[first] = elapsed(programs[first], query);
        ns[1-first] = elapsed(programs[1-first], query);
        printf("%d,%s,%d,%llu,%llu\n", repeat + 1, first ? "spatial-first" : "control-first",
               DRAWS, (unsigned long long)ns[0], (unsigned long long)ns[1]);
    }
    return EXIT_SUCCESS;
}

/* Time a synthetic shadow caster pass and its depth copy on the NVIDIA GPU. */
#define main sky_timer_main
#include "../task-18/sky_timer.c"
#undef main

struct shadow_target {
    int size;
    GLuint depth, copy, framebuffer;
};

static GLuint depth_texture(int size) {
    GLuint texture;
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, size, size, 0,
                 GL_DEPTH_COMPONENT, GL_UNSIGNED_SHORT, NULL);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    return texture;
}

static struct shadow_target shadow_target(int size) {
    struct shadow_target target = { .size = size };
    target.depth = depth_texture(size);
    target.copy = depth_texture(size);
    glGenFramebuffers(1, &target.framebuffer);
    glBindFramebuffer(GL_FRAMEBUFFER, target.framebuffer);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, target.depth, 0);
    glDrawBuffer(GL_NONE);
    glReadBuffer(GL_NONE);
    require(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE,
            "Incomplete shadow framebuffer");
    return target;
}

static GLuint alpha_atlas(void) {
    unsigned char pixels[8][8][4];
    memset(pixels, 255, sizeof(pixels));
    for (int y = 0; y < 8; y++) {
        for (int x = 0; x < 8; x++) {
            pixels[y][x][3] = (x + y) % 2 ? 255 : 0;
        }
    }
    GLuint texture;
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 8, 8, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels);
    return texture;
}

static void shadow_pass(const struct shadow_target *target, GLuint solid, GLuint cutout) {
    glClear(GL_DEPTH_BUFFER_BIT);
    glUseProgram(solid);
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
    glUseProgram(cutout);
    glDrawArrays(GL_TRIANGLE_STRIP, 4, 4);
    glCopyImageSubData(target->depth, GL_TEXTURE_2D, 0, 0, 0, 0,
                       target->copy, GL_TEXTURE_2D, 0, 0, 0, 0, target->size, target->size, 1);
}

static void select_shadow_target(const struct shadow_target *target) {
    glBindFramebuffer(GL_FRAMEBUFFER, target->framebuffer);
    glViewport(0, 0, target->size, target->size);
}

static void check_depth(const struct shadow_target *target, GLuint solid, GLuint cutout) {
    select_shadow_target(target);
    shadow_pass(target, solid, cutout);
    const int size = target->size;
    const int xs[] = {3 * size / 4, 5 * size / 32, 7 * size / 32};
    float depth[3];
    // Probe the solid floor, a hole in the cutout card, then the card itself.
    for (int i = 0; i < 3; i++) {
        glReadPixels(xs[i], size / 8 + size / 24, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, &depth[i]);
    }
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, target->copy, 0);
    for (int i = 0; i < 3; i++) {
        float copied;
        glReadPixels(xs[i], size / 8 + size / 24, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, &copied);
        require(depth[i] == copied, "Shadow depth copy probe failed");
    }
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, target->depth, 0);
    require(fabsf(depth[0] - .8f) < 2e-5f && fabsf(depth[1] - .8f) < 2e-5f
            && fabsf(depth[2] - .25f) < 2e-5f && glGetError() == GL_NO_ERROR,
            "Shadow solid/cutout depth probes failed");
    fprintf(stderr, "%d map depths %.3f %.3f %.3f\n", size, depth[0], depth[1], depth[2]);
}

static GLuint64 shadow_elapsed(const struct shadow_target *target, GLuint solid, GLuint cutout,
                               GLuint query) {
    select_shadow_target(target);
    glBeginQuery(GL_TIME_ELAPSED, query);
    for (int i = 0; i < DRAWS; i++) {
        shadow_pass(target, solid, cutout);
    }
    glEndQuery(GL_TIME_ELAPSED);
    GLuint64 ns;
    glGetQueryObjectui64v(query, GL_QUERY_RESULT, &ns);
    require(ns > 0 && glGetError() == GL_NO_ERROR, "Invalid shadow timer result");
    return ns;
}

int main(int argc, char **argv) {
    require(argc == 7, "Usage: shadow_timer solid.vert solid.frag cutout.vert cutout.frag full_size candidate_size");
    start_egl();
    fprintf(stderr, "%s | %s | %s\n", glGetString(GL_VENDOR), glGetString(GL_RENDERER),
            glGetString(GL_VERSION));
    const GLuint solid = program(argv[1], argv[2]), cutout = program(argv[3], argv[4]);
    GLint timer_bits;
    glGetQueryiv(GL_TIME_ELAPSED, GL_QUERY_COUNTER_BITS, &timer_bits);
    require(timer_bits >= 32, "GL_TIME_ELAPSED is unavailable");
    const struct shadow_target targets[] = {shadow_target(atoi(argv[5])), shadow_target(atoi(argv[6]))};
    glBindTexture(GL_TEXTURE_2D, alpha_atlas());
    glUseProgram(cutout);
    glUniform1i(glGetUniformLocation(cutout, "gtexture"), 0);
    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LESS);
    glColor4f(1, 1, 1, 1);
    const float positions[] = {
        -1,-1,.6f, 1,-1,.6f, -1,1,.6f, 1,1,.6f,
        -.75f,-.75f,-.5f, .25f,-.75f,-.5f, -.75f,.75f,-.5f, .25f,.75f,-.5f
    };
    const float uv[] = {0,0, 0,0, 0,0, 0,0, 0,0, 1,0, 0,1, 1,1};
    glEnableClientState(GL_VERTEX_ARRAY);
    glVertexPointer(3, GL_FLOAT, 0, positions);
    glEnableClientState(GL_TEXTURE_COORD_ARRAY);
    glTexCoordPointer(2, GL_FLOAT, 0, uv);
    GLuint query;
    glGenQueries(1, &query);
    for (int mode = 0; mode < 2; mode++) {
        check_depth(&targets[mode], solid, cutout);
        for (int warmup = 0; warmup < 8; warmup++) {
            shadow_elapsed(&targets[mode], solid, cutout, query);
        }
    }
    puts("scene,repeat,order,draws,off_ns,full_ns");
    for (int repeat = 0; repeat < REPEATS; repeat++) {
        const int first = repeat % 2;
        GLuint64 ns[2];
        ns[first] = shadow_elapsed(&targets[first], solid, cutout, query);
        ns[1-first] = shadow_elapsed(&targets[1-first], solid, cutout, query);
        printf("shadow-caster,%d,%s,%d,%llu,%llu\n", repeat + 1,
               first ? "full-first" : "off-first", DRAWS,
               (unsigned long long)ns[0], (unsigned long long)ns[1]);
    }
    return EXIT_SUCCESS;
}

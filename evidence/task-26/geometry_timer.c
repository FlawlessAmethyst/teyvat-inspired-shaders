/* Measure expanded forward shaders on controlled geometry. */
#define main sky_timer_main
#include "../task-18/sky_timer.c"
#undef main

static void bind_texture(int unit, int width, int height, GLint internal, GLenum format,
                         const float *data) {
    GLuint texture;
    glGenTextures(1, &texture);
    glActiveTexture(GL_TEXTURE0 + unit);
    glBindTexture(GL_TEXTURE_2D, texture);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexImage2D(GL_TEXTURE_2D, 0, internal, width, height, 0, format, GL_FLOAT, data);
}

static void inputs(int water) {
    const float atlas[] = {0.24f, 0.48f, 0.60f, 0.70f, 0.31f, 0.65f, 0.75f, 0.80f,
                           0.27f, 0.52f, 0.67f, 0.75f, 0.32f, 0.59f, 0.70f, 0.70f};
    const float light[] = {0.85f, 0.92f, 0.99f, 1.0f};
    bind_texture(0, 2, 2, GL_RGBA8, GL_RGBA, atlas);
    bind_texture(1, 1, 1, GL_RGBA8, GL_RGBA, light);
    if (!water)
        return;
    // Opaque background spans 8–17 blocks with a no-hit strip on one edge.
    size_t count = (size_t)WIDTH * HEIGHT;
    float *depth = malloc(count * sizeof(*depth));
    require(depth != NULL, "Cannot allocate opaque depth");
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            float distance = 8.0f + 9.0f * x / WIDTH;
            depth[(size_t)y * WIDTH + x] =
                x >= WIDTH * 9 / 10 ? 1.0f : (1.0f - 1.0f / distance) / (1.0f - 1.0f / 192.0f);
        }
    }
    bind_texture(2, WIDTH, HEIGHT, GL_DEPTH_COMPONENT32F, GL_DEPTH_COMPONENT, depth);
    free(depth);
}

static void shadow_texture(void) {
    const int size = 1024;
    float *depth = malloc((size_t)size * size * sizeof(*depth));
    require(depth != NULL, "Cannot allocate shadow depth");
    for (int y = 0; y < size; y++) {
        for (int x = 0; x < size; x++) {
            depth[y * size + x] = (x / 41 + y / 47) % 2 ? 0.40f : 0.78f;
        }
    }
    bind_texture(3, size, size, GL_DEPTH_COMPONENT32F, GL_DEPTH_COMPONENT, depth);
    free(depth);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_COMPARE_REF_TO_TEXTURE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC, GL_LEQUAL);
}

static void geometry_uniforms(GLuint id, int material, float rain, float sun_y, int submerged,
                              const GLfloat *rotation, const GLfloat *inverse_rotation,
                              const GLfloat *inverse_projection) {
    glUseProgram(id);
    glUniform1i(glGetUniformLocation(id, "gtexture"), 0);
    glUniform1i(glGetUniformLocation(id, "lightmap"), 1);
    glUniform1i(glGetUniformLocation(id, "depthtex2"), 2);
    glUniform1i(glGetUniformLocation(id, "shadowtex0"), 3);
    glUniform1i(glGetUniformLocation(id, "hasSkylight"), 1);
    glUniform1i(glGetUniformLocation(id, "isEyeInWater"), submerged);
    glUniform1f(glGetUniformLocation(id, "far"), 192.0f);
    glColor4f(0.70f, 0.90f, 0.65f, 1.0f);
    glUniform1f(glGetUniformLocation(id, "rainStrength"), rain);
    glUniform1f(glGetUniformLocation(id, "frameTimeCounter"), 60.0f);
    glUniform3f(glGetUniformLocation(id, "upPosition"), 0.0f, rotation[5], rotation[6]);
    glUniform3f(glGetUniformLocation(id, "sunPosition"), 0.0f,
                sun_y * rotation[5] - rotation[9], sun_y * rotation[6] - rotation[10]);
    glUniformMatrix4fv(glGetUniformLocation(id, "gbufferModelView"), 1, GL_FALSE, rotation);
    glUniformMatrix4fv(glGetUniformLocation(id, "gbufferModelViewInverse"), 1, GL_FALSE, inverse_rotation);
    glUniformMatrix4fv(glGetUniformLocation(id, "gbufferProjectionInverse"), 1, GL_FALSE, inverse_projection);
    // Project the test quad into a 128-block orthographic shadow view.
    const float shadow_projection[] = {
        1.0f/64,0,0,0, 0,1.0f/64,0,0, 0,0,-1.0f/64,0, 0,0,0,1
    };
    glUniformMatrix4fv(glGetUniformLocation(id, "shadowModelView"), 1, GL_FALSE, rotation);
    glUniformMatrix4fv(glGetUniformLocation(id, "shadowProjection"), 1, GL_FALSE, shadow_projection);
    GLint entity = glGetAttribLocation(id, "mc_Entity");
    if (entity >= 0)
        glVertexAttrib2f((GLuint)entity, (float)material, 0.0f);
}

static float check_draw(const GLuint *programs) {
    // Check that each timed setup rasterizes and retain a color-difference probe.
    float pixels[2][4][4];
    for (int mode = 0; mode < 2; mode++) {
        glUseProgram(programs[mode]);
        glClear(GL_COLOR_BUFFER_BIT);
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
        for (int point = 0; point < 4; point++) {
            glReadPixels((2 * point + 1) * WIDTH / 8, HEIGHT / 2, 1, 1,
                         GL_RGBA, GL_FLOAT, pixels[mode][point]);
            require(pixels[mode][point][2] > 0.0f, "Geometry probe missed a timed draw");
        }
    }
    require(glGetError() == GL_NO_ERROR, "Geometry probe failed");
    float difference = 0.0f;
    for (int point = 0; point < 4; point++) {
        for (int channel = 0; channel < 3; channel++) {
            difference = fmaxf(difference, fabsf(pixels[1][point][channel] - pixels[0][point][channel]));
        }
    }
    return difference;
}

int main(int argc, char **argv) {
    require(argc == 6 && (!strcmp(argv[1], "water") || !strcmp(argv[1], "fog")
                         || !strcmp(argv[1], "terrain")),
            "Usage: geometry_timer water|fog|terrain off.vert off.frag full.vert full.frag");
    const int water = !strcmp(argv[1], "water");
    const int terrain = !strcmp(argv[1], "terrain");
    start_egl();
    fprintf(stderr, "%s | %s | %s\n", glGetString(GL_VENDOR), glGetString(GL_RENDERER),
            glGetString(GL_VERSION));
    const GLuint programs[] = {program(argv[2], argv[3]), program(argv[4], argv[5])};
    GLint timer_bits;
    glGetQueryiv(GL_TIME_ELAPSED, GL_QUERY_COUNTER_BITS, &timer_bits);
    require(timer_bits >= 32, "GL_TIME_ELAPSED is unavailable");
    target();
    inputs(water);
    if (terrain)
        shadow_texture();
    const float top = tan(35.0 * pi / 180.0), right = top * WIDTH / HEIGHT, far = 192.0f;
    const float a = -(far + 1) / (far - 1), b = -2 * far / (far - 1);
    const float inverse_projection[] = {right,0,0,0, 0,top,0,0, 0,0,0,1/b, 0,0,-1,a/b};
    const float pitch = (water ? 12 : 4) * pi / 180.0, c = cosf(pitch), s = sinf(pitch);
    const float rotation[] = {1,0,0,0, 0,c,s,0, 0,-s,c,0, 0,0,0,1};
    const float inverse_rotation[] = {1,0,0,0, 0,c,-s,0, 0,s,c,0, 0,0,0,1};
    glMatrixMode(GL_PROJECTION);
    glFrustum(-right, right, -top, top, 1, far);
    glMatrixMode(GL_MODELVIEW);
    glClientActiveTexture(GL_TEXTURE0);
    const float uv[] = {0,0, 1,0, 0,1, 1,1};
    glEnableClientState(GL_VERTEX_ARRAY);
    glEnableClientState(GL_TEXTURE_COORD_ARRAY);
    glTexCoordPointer(2, GL_FLOAT, 0, uv);
    // Low block light and high skylight keep the terrain sun/receiver eligible.
    glMultiTexCoord2f(GL_TEXTURE1, 0.10f, 0.9f);
    glNormal3f(0, c, s);
    if (water) {
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    }

    const struct test_case { const char *name; float z, rain, sun_y; int submerged, material; }
    water_cases[] = {
        {"water-clear", 7, 0, 2.0f, 0, 10001}, {"water-rain", 7, 1, 2.0f, 0, 10001},
        {"water-under", 7, 0, 2.0f, 1, 10001}
    }, fog_cases[] = {
        {"fog-near", 16, 0, 2.0f, 0, 0}, {"fog-clear", 110, 0, 2.0f, 0, 0},
        {"fog-dusk", 110, 0, 0.12f, 0, 0}, {"fog-rain", 80, 1, 2.0f, 0, 0},
        {"fog-under", 14, 0, 2.0f, 1, 0}
    }, terrain_cases[] = {
        {"foliage-lit", 24, 0, 2.0f, 0, 10002},
        {"foliage-range-fade", 46, 0, 2.0f, 0, 10002},
        {"stone-night", 24, 0, -2.0f, 0, 0}
    };
    const struct test_case *cases = water ? water_cases : terrain ? terrain_cases : fog_cases;
    size_t case_count = water ? sizeof(water_cases) / sizeof(*cases)
                              : terrain ? sizeof(terrain_cases) / sizeof(*cases)
                                        : sizeof(fog_cases) / sizeof(*cases);
    GLuint query;
    glGenQueries(1, &query);
    puts("scene,repeat,order,draws,off_ns,full_ns");
    for (size_t i = 0; i < case_count; i++) {
        const struct test_case scene = cases[i];
        float x = right * scene.z, y = top * scene.z, z = -scene.z;
        const float quad[] = {-x,-y,z, x,-y,z, -x,y,z, x,y,z};
        glVertexPointer(3, GL_FLOAT, 0, quad);
        for (int mode = 0; mode < 2; mode++)
            geometry_uniforms(programs[mode], scene.material, scene.rain, scene.sun_y, scene.submerged,
                              rotation, inverse_rotation, inverse_projection);
        fprintf(stderr, "%s max sampled linear RGB delta %.6f\n", scene.name, check_draw(programs));
        for (int warmup = 0; warmup < 8; warmup++) {
            elapsed(programs[0], query);
            elapsed(programs[1], query);
        }
        for (int repeat = 0; repeat < REPEATS; repeat++) {
            int first = repeat % 2;
            GLuint64 ns[2];
            ns[first] = elapsed(programs[first], query);
            ns[1-first] = elapsed(programs[1-first], query);
            printf("%s,%d,%s,%d,%llu,%llu\n", scene.name, repeat + 1,
                   first ? "full-first" : "off-first", DRAWS,
                   (unsigned long long)ns[0], (unsigned long long)ns[1]);
        }
    }
    return EXIT_SUCCESS;
}

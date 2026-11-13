#version 330 compatibility

uniform sampler2D gtexture;
in vec2 casterUV;
in float casterAlpha;

/* DRAWBUFFERS: */

void main() {
    // Coarser atlas mips fill small holes before depth filtering can see them.
    if (textureLod(gtexture, casterUV, 0.0).a * casterAlpha <= 0.1) {
        discard;
    }
}

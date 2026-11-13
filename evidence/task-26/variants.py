#!/usr/bin/env python3
"""Build TASK-26 ablations from the exact accepted shader tree."""
import hashlib
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHADERS = ROOT / 'artifacts/task-25-fog-tuning/shaders'
MANIFEST = ROOT / 'evidence/task-25/fog-pack.sha256'

# Each entry specifies the scenes where the removed work is visible.
SCENES = {
    'sodium': ('valley', 'rain', 'grove', 'shallows', 'cave'),
    'full': ('valley', 'rain', 'grove', 'shallows', 'cave'),
    'shadowless': ('valley', 'grove'),
    'cloudless': ('valley', 'rain'),
    'fogless': ('valley', 'rain'),
    'water-depthless': ('shallows',),
    'water-vanilla': ('shallows',),
    'gradeless': ('valley', 'cave'),
    'terrain-vanilla': ('grove',),
    'rain-neutral': ('rain',),
}
# The second round reverses the first to bracket the variants with full runs.
MODES = tuple(SCENES)


def tree_manifest(shaders):
    rows = []
    for path in sorted(shaders.rglob('*')):
        if path.is_file():
            with path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            rows.append(f'{digest}  {path.relative_to(shaders)}\n')
    return ''.join(rows)


def edit(shaders, name, before, after):
    path = shaders / name
    source = path.read_text()
    if source.count(before) != 1:
        raise RuntimeError(f'{path}: expected exactly one match for {before!r}')
    path.write_text(source.replace(before, after))


def apply(shaders, mode):
    if mode in ('shadowless', 'terrain-vanilla'):
        properties = shaders / 'shaders.properties'
        with properties.open('a') as stream:
            stream.write('\n# TASK-26 developer ablation\nshadow.enabled=false\n')
        edit(shaders, 'lib/geometry_vertex.glsl',
             '    vertexShadowReceiver(viewPosition, facing, sunElevation, outdoors);\n', '')
        edit(shaders, 'lib/geometry_fragment.glsl',
             'terrainSunVisibility(fogViewPosition, terrainDirectLight.r)', '1.0')
    if mode == 'terrain-vanilla':
        for ext in ('vsh', 'fsh'):
            edit(shaders, f'gbuffers_terrain.{ext}', '#define TERRAIN_LIGHTING\n', '')
    if mode == 'cloudless':
        edit(shaders, 'gbuffers_skybasic.fsh',
             '            vec2 cloud = sampleCloudDeck(cloudWorldRay, elevation, cloudPlane,\n'
             '                                         cloudLightDirection, rainStrength);\n'
             '            color = mix(color, cloudColor(cloud.y, skySunwardWeight(sunFacing),\n'
             '                                         cloudBase, cloudRim, rainStrength), cloud.x);\n', '')
        edit(shaders, 'gbuffers_skybasic.fsh',
             '            float elevation = dot(normalize(viewRay), skyUp);\n'
             '            float cloudOpacity = sampleCloudDeck(cloudWorldRay, elevation, cloudPlane,\n'
             '                                                 cloudLightDirection, rainStrength).x;\n', '')
        edit(shaders, 'gbuffers_skybasic.fsh', ' * (1.0 - cloudOpacity)', '')
    if mode == 'fogless':
        # Stub only the color term. View-space inputs also serve shadows and water.
        path = shaders / 'lib/fog.glsl'
        source = path.read_text()
        head, marker, _ = source.partition('    float distanceSquared =')
        if not marker:
            raise RuntimeError(f'{path}: missing fog body')
        path.write_text(head + '    return color;\n}\n')
    if mode == 'water-depthless':
        # Match the shader's missing-background fallback with uniform absorption.
        edit(shaders, 'lib/water.glsl', '    float thickness = waterThickness(viewRay);',
             '    float thickness = -1.0;')
    if mode == 'water-vanilla':
        for ext in ('vsh', 'fsh'):
            edit(shaders, f'gbuffers_water.{ext}', '#define STYLIZED_WATER\n', '')
    if mode == 'gradeless':
        edit(shaders, 'final.fsh', 'gradeSceneColor(sceneColor, saturationBoost)', 'sceneColor')
    if mode == 'rain-neutral':
        for name in ('lib/geometry_vertex.glsl', 'lib/water.glsl',
                     'gbuffers_skybasic.vsh', 'gbuffers_skybasic.fsh', 'final.vsh'):
            path = shaders / name
            source = path.read_text()
            if source.count('rainStrength') < 2:
                raise RuntimeError(f'{path}: missing rain uniform or uses')
            path.write_text(source.replace('uniform float rainStrength;', '')
                            .replace('rainStrength', '0.0'))
        edit(shaders, 'gbuffers_weather.fsh', '#define WEATHER_COLOR\n', '')


def build(root):
    expected = MANIFEST.read_text().replace('  shaderpack/shaders/', '  ')
    if tree_manifest(SHADERS) != expected:
        raise RuntimeError('The retained shader tree differs from the TASK-25 fog manifest')
    for mode in MODES[1:]:
        folder = root / 'variants' / mode
        shaders = folder / 'shaders'
        shutil.copytree(SHADERS, shaders)
        apply(shaders, mode)
        (folder / 'pack.sha256').write_text(tree_manifest(shaders))

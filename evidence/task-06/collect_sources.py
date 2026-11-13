from pathlib import Path
import hashlib,json,subprocess,zipfile
out=Path('evidence/task-06')
repos={}
for name,folder,url in [('iris','iris-source','https://github.com/IrisShaders/Iris'),('docs','iris-docs','https://github.com/IrisShaders/DocsPage')]:
 p=Path('artifacts/task-06')/folder
 repos[name]={'url':url,'revision':subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip(),'local_path':str(p)}
docs=['Reference/Programs/'+n+'.mdx' for n in ['gbuffers','shadow','deferred','composite','final']]+['Reference/Buffers/'+n+'.mdx' for n in ['colortex','depthtex','shadowtex','atlases']]+['Reference/Attributes/'+n+'.mdx' for n in ['gl_Color','gl_MultiTexCoord1','mc_Entity','at_midBlock']]+['Reference/Uniforms/'+n+'.mdx' for n in ['world','biome','matrices','camera','system']]+['Reference/Miscellaneous/'+n+'.mdx' for n in ['block_properties','dimension_properties','include']]+['Reference/Shaders.Properties/features.mdx','How To/compatibility_vs_core.mdx']
src=['pipeline/IrisRenderingPipeline.java','samplers/IrisSamplers.java','uniforms/CommonUniforms.java','uniforms/IrisExclusiveUniforms.java','uniforms/WorldTimeUniforms.java','uniforms/MatrixUniforms.java','uniforms/CelestialUniforms.java','shaderpack/ShaderPack.java','pipeline/programs/SodiumPrograms.java','pipeline/transform/transformer/SodiumTransformer.java','pathways/colorspace/ColorSpaceFragmentConverter.java','pathways/colorspace/ColorSpaceComputeConverter.java']
records=[]
from urllib.parse import quote
for repo,paths,prefix in [('docs',docs,'src/content/docs/current/'),('iris',src,'common/src/main/java/net/irisshaders/iris/')]:
 for f in paths:
  rel=prefix+f;p=Path(repos[repo]['local_path'])/rel
  records.append({'repository':repo,'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'url':repos[repo]['url']+'/blob/'+repos[repo]['revision']+'/'+quote(rel)})
jar=next((Path.home() / '.var/app/org.prismlauncher.PrismLauncher/data/PrismLauncher/instances/GenshinShaderDev/minecraft/mods').glob('iris-*.jar'))
with zipfile.ZipFile(jar) as z:
 metadata=z.read('META-INF/neoforge.mods.toml').decode()
 checks={}
 for cls,terms in {'uniforms/CommonUniforms':['rainStrength','wetness','isEyeInWater'],'uniforms/MatrixUniforms':['gbufferProjectionInverse','shadowModelView'],'samplers/IrisSamplers':['depthtex1','shadowtex0'],'pipeline/IrisRenderingPipeline':['copyPreTranslucentDepth','beginTranslucents'],'pipeline/programs/SodiumPrograms':['at_midBlock','mc_Entity'],'shaderpack/ShaderPack':['dimension.properties']}.items():
  data=z.read('net/irisshaders/iris/'+cls+'.class')
  checks[cls]={s:s.encode() in data for s in terms}
(out/'sources.json').write_text(json.dumps({'accessed':'2026-11-12','repositories':repos,'files':records,'installed_jar':{'path':str(Path('~') / jar.relative_to(Path.home())),'sha256':hashlib.sha256(jar.read_bytes()).hexdigest(),'metadata':metadata,'constant_pool_presence_only':checks},'limits':'Branch revision is not proven to build the installed beta. Class byte strings establish names only, not semantics or runtime results.'},indent=2)+'\n')
print('Recorded',len(records),'source files and installed JAR metadata/symbol presence')

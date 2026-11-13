# White receiver pad for isolated casters, with a range lane to the east.
fill 1008 182 1027 1033 182 1040 minecraft:smooth_stone
fill 1026 182 1040 1096 182 1049 minecraft:smooth_stone
setblock 1017 183 1029 minecraft:chest[facing=west]
setblock 1017 185 1032 minecraft:oak_leaves[persistent=true]
fill 1017 183 1035 1017 186 1035 minecraft:stone
fill 1017 183 1038 1017 184 1038 minecraft:glass
fill 1048 183 1047 1048 187 1047 minecraft:stone
fill 1065 183 1046 1065 187 1046 minecraft:stone
fill 1077 183 1045 1077 187 1045 minecraft:stone
fill 1085 183 1044 1085 187 1044 minecraft:stone
fill 1093 183 1043 1093 187 1043 minecraft:stone
execute if block 1017 183 1029 minecraft:chest if block 1017 185 1032 minecraft:oak_leaves if block 1017 184 1038 minecraft:glass if block 1093 187 1043 minecraft:stone run tellraw @s {"text":"TASK16_READY_FIXTURE"}

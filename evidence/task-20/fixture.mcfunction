# Keep the TASK-03 camera presets untouched. Build east of their test platform.
fill 1051 180 990 1090 182 1026 minecraft:stone
fill 1051 182 990 1090 182 1026 minecraft:grass_block
fill 1051 183 990 1090 196 1026 minecraft:air
fillbiome 1048 180 988 1091 195 1007 minecraft:plains
fillbiome 1048 180 1008 1091 195 1027 minecraft:jungle

# Paired oak crowns and understory on the two sides of the biome boundary.
fill 1061 186 1001 1065 188 1005 minecraft:oak_leaves[persistent=true]
fill 1061 189 1002 1064 189 1004 minecraft:oak_leaves[persistent=true]
fill 1063 183 1003 1063 188 1003 minecraft:oak_log
fill 1061 186 1011 1065 188 1015 minecraft:oak_leaves[persistent=true]
fill 1061 189 1012 1064 189 1014 minecraft:oak_leaves[persistent=true]
fill 1063 183 1013 1063 188 1013 minecraft:oak_log
setblock 1059 183 1005 minecraft:short_grass
setblock 1059 183 1011 minecraft:short_grass
setblock 1062 183 1005 minecraft:tall_grass[half=lower]
setblock 1062 184 1005 minecraft:tall_grass[half=upper]
setblock 1062 183 1011 minecraft:tall_grass[half=lower]
setblock 1062 184 1011 minecraft:tall_grass[half=upper]
setblock 1061 183 1006 minecraft:fern
setblock 1061 183 1010 minecraft:fern
setblock 1064 183 1007 minecraft:large_fern[half=lower]
setblock 1064 184 1007 minecraft:large_fern[half=upper]

# Overlapping canopies create self-shadowed interiors and varied cutout edges.
fill 1066 187 1004 1071 190 1009 minecraft:jungle_leaves[persistent=true]
fill 1067 191 1005 1070 191 1008 minecraft:jungle_leaves[persistent=true]
fill 1069 183 1007 1069 190 1007 minecraft:jungle_log
fill 1067 188 1010 1072 191 1016 minecraft:spruce_leaves[persistent=true]
fill 1068 192 1011 1071 192 1015 minecraft:spruce_leaves[persistent=true]
fill 1070 193 1012 1070 193 1014 minecraft:spruce_leaves[persistent=true]
fill 1070 183 1013 1070 191 1013 minecraft:spruce_log
fill 1071 188 997 1077 191 1004 minecraft:birch_leaves[persistent=true]
fill 1072 192 998 1076 192 1003 minecraft:birch_leaves[persistent=true]
fill 1074 183 1001 1074 191 1001 minecraft:birch_log
fill 1073 186 1005 1081 189 1012 minecraft:dark_oak_leaves[persistent=true]
fill 1075 190 1006 1079 191 1011 minecraft:dark_oak_leaves[persistent=true]
fill 1076 183 1008 1077 189 1009 minecraft:dark_oak_log
fill 1076 188 1013 1081 190 1019 minecraft:cherry_leaves[persistent=true]
fill 1077 191 1014 1080 191 1018 minecraft:cherry_leaves[persistent=true]
fill 1079 183 1016 1079 190 1016 minecraft:cherry_log

# Neutral path and raised camera perch give controls for material and cast shadows.
fill 1053 182 1008 1085 182 1009 minecraft:stone_bricks
fill 1054 183 1008 1054 191 1008 minecraft:stone
execute if block 1054 191 1008 minecraft:stone if block 1062 184 1011 minecraft:tall_grass[half=upper] if block 1064 184 1007 minecraft:large_fern[half=upper] if block 1079 191 1018 minecraft:cherry_leaves if biome 1063 187 1003 minecraft:plains if biome 1063 187 1013 minecraft:jungle run tellraw @s {"text":"TASK03_READY_build"}

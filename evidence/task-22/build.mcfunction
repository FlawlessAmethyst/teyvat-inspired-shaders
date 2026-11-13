# Run only in the disposable TASK-22 world, after its initial daylight preset.
execute in minecraft:overworld run tp @s 958.5 184 1052.5 0 0
fill 943 183 1049 957 191 1071 minecraft:stone
fill 944 184 1050 956 189 1070 minecraft:air
fill 944 183 1050 956 183 1070 minecraft:stone_bricks
fill 944 184 1069 956 184 1069 minecraft:deepslate_tiles
fill 944 184 1061 944 187 1068 minecraft:polished_andesite
fill 956 184 1061 956 187 1068 minecraft:polished_andesite
setblock 946 184 1061 minecraft:lantern
setblock 954 184 1061 minecraft:soul_lantern
setblock 950 186 1070 minecraft:sea_lantern
setblock 947 186 1070 minecraft:shroomlight
setblock 953 186 1070 minecraft:glowstone
fill 962 183 1049 976 191 1071 minecraft:stone
fill 963 184 1050 975 189 1070 minecraft:air
fill 963 183 1050 975 183 1070 minecraft:stone_bricks
fill 966 184 1058 972 184 1061 minecraft:polished_andesite
fill 966 185 1060 972 185 1061 minecraft:polished_andesite
fill 963 184 1064 965 187 1066 minecraft:deepslate_tiles
fill 973 184 1064 975 187 1066 minecraft:oak_planks
execute in minecraft:the_nether run forceload add 0 0
execute in minecraft:the_end run forceload add 0 37
tellraw @s {"text":"TASK03_READY_build"}

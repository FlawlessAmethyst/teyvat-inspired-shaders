gamemode creative @s
gamerule doDaylightCycle false
gamerule doWeatherCycle false
gamerule doMobSpawning false
gamerule randomTickSpeed 0
gamerule doFireTick false
gamerule doInsomnia false
gamerule sendCommandFeedback false
difficulty peaceful
effect clear @s
clear @s
execute in minecraft:overworld run tp @s 1000.5 184 1036.5 180 8
fill 950 179 950 1050 181 1050 minecraft:stone
fill 950 182 950 1050 182 1050 minecraft:grass_block
fill 950 183 950 1050 185 1050 minecraft:air
fillbiome 944 180 944 975 207 975 minecraft:plains
fillbiome 944 180 976 975 207 1007 minecraft:plains
fillbiome 944 180 1008 975 207 1039 minecraft:plains
fillbiome 944 180 1040 975 207 1071 minecraft:plains
fillbiome 976 180 944 1007 207 975 minecraft:plains
fillbiome 976 180 976 1007 207 1007 minecraft:plains
fillbiome 976 180 1008 1007 207 1039 minecraft:plains
fillbiome 976 180 1040 1007 207 1071 minecraft:plains
fillbiome 1008 180 944 1039 207 975 minecraft:plains
fillbiome 1008 180 976 1039 207 1007 minecraft:plains
fillbiome 1008 180 1008 1039 207 1039 minecraft:plains
fillbiome 1008 180 1040 1039 207 1071 minecraft:plains
fillbiome 1040 180 944 1071 207 975 minecraft:plains
fillbiome 1040 180 976 1071 207 1007 minecraft:plains
fillbiome 1040 180 1008 1071 207 1039 minecraft:plains
fillbiome 1040 180 1040 1071 207 1071 minecraft:plains
fill 958 180 960 990 181 1018 minecraft:sand
fill 958 182 960 990 182 1018 minecraft:water
fill 1002 187 984 1006 190 988 minecraft:oak_leaves[persistent=true]
fill 1004 183 986 1004 189 986 minecraft:oak_log
fill 1011 188 978 1015 191 982 minecraft:oak_leaves[persistent=true]
fill 1013 183 980 1013 190 980 minecraft:oak_log
fill 1020 186 985 1024 189 989 minecraft:oak_leaves[persistent=true]
fill 1022 183 987 1022 188 987 minecraft:oak_log
fill 1029 189 974 1033 192 978 minecraft:oak_leaves[persistent=true]
fill 1031 183 976 1031 191 976 minecraft:oak_log
fill 1005 187 967 1009 190 971 minecraft:oak_leaves[persistent=true]
fill 1007 183 969 1007 189 969 minecraft:oak_log
fill 1018 188 958 1022 191 962 minecraft:oak_leaves[persistent=true]
fill 1020 183 960 1020 190 960 minecraft:oak_log
fill 1031 187 959 1035 190 963 minecraft:oak_leaves[persistent=true]
fill 1033 183 961 1033 189 961 minecraft:oak_log
fill 1036 186 986 1040 189 990 minecraft:oak_leaves[persistent=true]
fill 1038 183 988 1038 188 988 minecraft:oak_log
fill 1025 187 998 1029 190 1002 minecraft:oak_leaves[persistent=true]
fill 1027 183 1000 1027 189 1000 minecraft:oak_log
fill 995 183 953 1001 194 960 minecraft:stone
fill 985 183 945 997 202 952 minecraft:stone
fill 1002 183 1005 1010 183 1012 minecraft:moss_block
fill 1017 183 1010 1023 186 1016 minecraft:stone_bricks
fill 960 183 1023 980 192 1045 minecraft:stone
fill 962 184 1025 978 189 1043 minecraft:air
fill 967 184 1023 971 187 1024 minecraft:air
setblock 964 184 1038 minecraft:lantern
setblock 976 184 1040 minecraft:lantern
fill 963 184 1030 964 187 1031 minecraft:stone
fill 975 184 1034 976 188 1035 minecraft:stone
time set 6000
weather clear 1000000
tellraw @s {"text":"TASK03_READY_build"}

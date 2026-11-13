# Same pale floor material under all four depth steps. The surface stays at Y=182.
fill 1007 175 1028 1047 182 1046 minecraft:smooth_sandstone
fill 1007 183 1028 1047 185 1046 minecraft:air
fill 1009 182 1029 1016 182 1045 minecraft:water
fill 1017 181 1029 1024 182 1045 minecraft:water
fill 1025 179 1029 1032 182 1045 minecraft:water
fill 1033 176 1029 1045 182 1045 minecraft:water
# Bottom stripes and lamps make the visibility of each step easy to compare.
fill 1013 181 1035 1013 181 1040 minecraft:sandstone
fill 1020 180 1035 1020 180 1040 minecraft:sandstone
fill 1028 178 1035 1028 178 1040 minecraft:sandstone
fill 1037 175 1035 1037 175 1040 minecraft:sandstone
setblock 1028 178 1037 minecraft:sea_lantern
setblock 1037 175 1037 minecraft:sea_lantern
# Stained glass on each side of the shoreline. The farther panel overlaps water.
fill 1008 183 1031 1008 184 1033 minecraft:orange_stained_glass
fill 1014 183 1040 1014 184 1043 minecraft:purple_stained_glass
execute if block 1009 182 1037 minecraft:water if block 1040 176 1037 minecraft:water if block 1013 181 1036 minecraft:sandstone if block 1037 175 1037 minecraft:sea_lantern if block 1014 184 1043 minecraft:purple_stained_glass run tellraw @s {"text":"TASK03_READY_build"}

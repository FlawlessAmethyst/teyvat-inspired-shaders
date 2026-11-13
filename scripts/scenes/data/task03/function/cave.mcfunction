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
execute in minecraft:overworld run tp @s 970.5 184 1027.5 0 3
time set 6000
weather clear 1000000
tellraw @s {"text":"TASK03_READY_cave"}

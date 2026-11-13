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
execute in minecraft:overworld run tp @s 974.5 183 1020.5 180 5
time set 6000
weather clear 1000000
tellraw @s {"text":"TASK03_READY_open-water"}

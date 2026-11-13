execute store result score #base task03 run fill 1001 183 1028 1006 183 1031 minecraft:snow_block replace minecraft:air
execute store result score #step task03 run fill 1001 184 1028 1003 184 1029 minecraft:snow_block replace minecraft:air
execute if score #base task03 matches 24 if score #step task03 matches 6 run tellraw @s {"text":"TASK11_SNOW_PLACED_24_6"}
scoreboard players reset #base task03
scoreboard players reset #step task03
tp @s 1003.5 183 1035.5 180 18

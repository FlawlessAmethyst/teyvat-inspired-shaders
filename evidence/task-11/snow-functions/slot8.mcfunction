scoreboard players set @s task03 8
execute store success score #snow task03 positioned 970.5 184 1027.5 if entity @s[distance=..2]
execute if score #snow task03 matches 1 run function task03:snow_show
execute if score #snow task03 matches 0 run function task03:snow_hide
scoreboard players reset #snow task03

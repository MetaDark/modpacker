#!/usr/bin/env python3

from source.curseforge import CurseForge
from source.micdoodle8 import Micdoodle8
from source.optifine import OptiFine
from source.pixelmon_reforged import PixelmonReforged

curse_forge = CurseForge()
print(curse_forge.url())

invtweaks = curse_forge.mod('inventory-tweaks')
print(invtweaks.url())
print(invtweaks.doc())
print(invtweaks.latest('1.12.2'))

jei = curse_forge.mod('jei')
print(jei.url())
print(jei.doc())
print(jei.latest('1.12.2'))

micdoodle8 = Micdoodle8()
print(micdoodle8.url())
galacticraft = micdoodle8.mod('galacticraft')
print(galacticraft.url())
print(galacticraft.doc())
print(galacticraft.latest('1.12.2'))

optifine = OptiFine()
print(optifine.url())
print(optifine.doc())
print(optifine.latest('1.12.2'))

pixelmon = PixelmonReforged()
print(pixelmon.url())
print(pixelmon.doc())
print(pixelmon.latest('1.12.2'))

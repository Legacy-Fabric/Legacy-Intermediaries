Legacy-Intermediaries
------------------------

## Hydos's guide on how to use the toolchain on legacy versions (subject to change)
1. Clone legacy fabric matcher
2. generate a config using the config generator i made (because it's simple. may not work on macos/linux as its untested)
3. Auto match all
4. match as much as you can definitley confirm is the same class
5. if the match is less than ~70% on classes, then keep matching
6. save the matches to the repository
7. invert matches somehow (i wrote a program for it. i recommend you do the same)
8. run stitch's updateIntermediary task
9. clone yarn and create a new branch
10. change yarn's version to the version you created intermediaries for and run `gradlew yarn`
11. if there are conflicts, go through and fix those (delete lines with the conflicts. this seams to be the best option)
12. if yarn runs, then you updated intermediaries Successfully! your next job is to follow https://fabricmc.net/wiki/tutorial:updating_yarn#updating_yarn 
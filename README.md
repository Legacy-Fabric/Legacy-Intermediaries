# Legacy-intermediary mappings

This repository contains the match information between different versions of Minecraft created by the LegacyFabric project, as well as the "intermediary" mappings we use, that is an intermediary naming form which tries to keep names
the same across versions and mapping changes.

## Files included in this repo

* __mappings/<mcversion>.tiny__: Intermediary mappings in the Tiny mapping format.
* __matches/releases/gameversion/*.matches__: Matches between Minecraft versions, created by the LegacyFabric project with the aid of Matcher.

## Generating / updating mappings

In general, you're going to want to use the following tools:

* [Matcher](https://github.com/FabricMC/Matcher) by sfPlayer1 can be used to create a match file between two JARs. In addition, it can load Enigma-format mappings, which can be used as an aid in figuring out changes.
* [Stitch](https://github.com/FabricMC/stitch) is a toolset for generating mappings based on match files. "generateIntermediary" is used to start a fresh chain of intermediary mappings, while "updateIntermediary" is used to add a new entry to the chain based on the previous entry and a matches file.

## License

As with the named mappings, we provide the intermediary mappings under the Creative Commons Zero license, so all can benefit.

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
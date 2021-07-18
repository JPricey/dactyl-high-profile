# Yet another Dactyl Manuform Spinoff

![Photo](https://i.redd.it/ljnm9ia2v0c71.jpg)

This repo is a re-implementation of the [Dactyl Manuform Tight](https://github.com/okke-formsma/dactyl-manuform-tight) in python, with a few of my own changes.

There are some hacks in here to get the border walls and thumb cluster to line up properly at the current tenting angle and key layout.
I didn't build this script with the goal of making it easy to share and extend... so if you're using this repo as a starting point for your own dactyl build, good luck, and beware of some shard edges.

## Generating OpenSCAD Models
This script is tested against Python 3.8.0

Intall dependencies with `pip install -r requirements.txt`

Run a one-off scad model build with `make run`

Watch and rebuild scad models with `make watch` (useful for development)

# Design Decisions (as of 4/29)

## Direction

When I started planning the computer vision work, I spent some time thinking about whether the scanner should be completely automatic or guided. While a fully automatic scanner sounds ideal at first (user shows the cube in any random orientation and the system figures everything out), it's not a very practical approach to this project as it introduces a lot of complexity all at once - orientation inference, way less deterministic face mapping, and much harder debugging.

So the direction I'm going in for this project is guided scanning. That means the user will still get a mostly automatic computer vision pipeline, but they'll follow simple prompts for how to hold the cube. The tradeoff is a little more user involvement, but the benefit is dramatically better reliability and much clearer logic for cube reconstruction. 

Manual input will still be an option for users. It's not only helpful for users without camera support, but is a good safety net while I work on implementing vision features. 

## Building on what we have

I've already implemented the current solver architecture, and it will require minimal changes in the future, since we are building our computer vision pipeline right on top of it. The files in 'src/' are already doing the right core work, so the vision component doesn't need to reinvent solving logic. Its job is much narrow and cleaner: producing a correct cube state in the same format the solver system already understands.

To put it simply, the CV scanner is a new input pipeline that reuses the existing backbone:
- Acquire cube state from camera
- Convert it into the same face dictionary currently used by manual input
- Reuse existing validation, solver, and playback unchanged whenever possible

I am open, of course, to suggestions for this approach. Simply leave a comment on documentation-related pull requests or create an issue. Any suggestions however, should keep the architecture modular.

## User Experience

The end goal is a CLI-like flow that feels like a natural extension to our program right now The user will choose between manual mode and camera mode. If they choose camera mode, the app opens a preview window and gives clear instructions for the first corner scan ('U/F/R') and then the opposite corner scan ('D/B/L'), see below. After each scan, the program shows what it detected and prompts the user to accept or re-scan. If both scans are accepted, the program reconstructs the full cube, validates it, solves it, and then hands it off to the playback mechanism already in place.

![alt text](image.png)

Note: The animation library is to be determined, but I am considering AnimCubeJS because it's an interactive animation. It renders it in the browser. I know little of front-end work so maybe browsers will be difficult to work with, let me know.

## Scanning the Cube (Important!)

The scanner will be based on color detection and face normalization (since the tiles of the cube will be angled).
Essentially, we will:
- detect tile-like regions in the frame
- group them into three visible faces
- normalize each face with perspective correction
- sample a 3 x 3 grid from each normalized face
- classify colors across all 54 sampled tiles
- map those color classes to `U/R/F/D/L/B` labels
- merge the two scans into one full cube state

This design is practical in my opinion because it aligns with what the current code expects the cube data to be like.

## Perspective Warp

A face seen at an angle is distorted in camera space If we try to index the tiles directly from that distorted view, that may introduce a lot of bugs. A perspective transform that lets us map each detected face into a standard square image where tile positions are predictable makes sampling the 3 x 3 grid become deterministic.

## Color Strategy

I'm unsure how I want to approach this. There was a suggestion to train our own model off of Kaggle datasets, but that approach may be fragile due to varying lighting conditions from users. 

From what I've researched, it seems a good solution would be to gather all sampled tile colors from both scans and cluster similar shades into six groups. We don't immediately care if a cluster is called 'U' or 'R', we first make sure similar colors are grouped together reliably. After grouping, we assign names to those six clusters using the cube's center tiles and the guided scan orientation. 

We need to avoid reading a tile from just one pixel, since cameras pick up a lot of noise. Glare can make a single pixel very misleading. Instead, I think we should average a small region near the center of each tile, which is much more stable.

As for handling similar colors like red and orange, I don't know if it's worth it to address this issue. If we were to address it though, I think we should implement some sort of confidence scale. If a grouping looks uncertain, then we prompt the user for a re-scan instead of potentially solving the wrong cube.

## Vision Module

I've made a vision module with the following responsibilities:
- `camera.py` for frame capture
- `ui_overlay.py` for live guidance and diagnostic overlays
- `sticker_detector.py` for contour-based sticker candidate detection
- `face_grouping.py` for grouping candidates into three visible faces
- `face_geometry.py` for corner estimation and canonical point ordering
- `warp_sampling.py` for perspective transform and grid sampling
- `color_model.py` for color features, clustering, and confidence(?)
- `face_labeling.py` for mapping colors to `U/R/F/D/L/B`
- `scan_fusion.py` for merging first and second scans
- `scan_validation.py` for quality checks before solve
- `scanner.py` for orchestrating the complete scan flow


## Suggestions

Please give any suggestions below. 

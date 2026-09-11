# Cube Vision Dataset Card

This repository ships a schema and capture protocol, not fabricated camera
observations. Populate `data/manifest_template.csv` while collecting real cubes.

Each row represents one complete labeled observation and records its session,
scramble, camera, environmental conditions, frame location, and canonical
54-character ground truth in `URFDLB` face order.

## Collection checklist

1. Generate and save a legal scramble and its resulting canonical state.
2. Apply that exact scramble to the physical cube.
3. Record the two prescribed corner views without changing sticker state.
4. Label lighting, distance, angle, glare, background, cube, and camera.
5. Review orientation and ground truth before accepting the record.
6. Run manifest validation and keep session/scramble groups within one split.

Camera imagery can contain people or private background information. Obtain
consent, minimize the field of view, and inspect images before sharing them.

# Revival AR · Llandough (v0.2.1)

Four places on the hill at Llandough, rebuilt from the records and pinned where they stood:
Iron Age roundhouse, Roman villa, early medieval monastery (cemetery and pillar cross) and Tŷ Mawr.

- `index.html` — map (you-are-here + distance to each pin), 3D / AR view (WebXR, Scene Viewer, Quick Look via model-viewer), 12-stop tour (en; cy/es outline).
- `SITES.json` — each site's position, confidence, what is known (with sources) and what is estimated.
- `tour.json` — the chronology as walking-tour stops, in the site's period order.
- `models/*.glb` — the reconstructions (metres; +x east, +y up, +z south; origin = the pin). Built by `tools/build_models.py` (no generated imagery).

Rule: shapes and positions only from records (Heneb HER, RCAHMW Coflein, Holbrook & Thomas 2005 Fig. 2, the 1824 survey tracing, reference photographs). Anything else is listed under `estimated` and shown as “reconstruction — estimated”.

Preview (branch build): https://section-revival-ar.cedwyn-274.pages.dev/

— Sion's Tab agent

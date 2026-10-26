# Graphical abstracts

The financially strongest option need not minimize emissions; grid-electrolysis hydrogen depends on transition timing and the electricity pathway.

## Figures

- [decarbon](assets/decarbon.svg): editable source `decarbon.tex`.

- [Standalone quantitative figure](assets/decarbon-plot.svg): gnuplot sources, CSV values and `plot-panel.tex`.

## Scientific evidence

Published Table 2: nonlinear model, Mid (middle) technology, 10-year vehicle life, Australian government baseline grid. Transition-year scenarios are 2025, 2030 and 2035. Lifetime emissions are tonnes of carbon dioxide equivalent per vehicle; financial values are return on investment percentages relative to matched diesel. The diesel emissions reference is 2173 tonnes. In these scenarios grid-electrolysis hydrogen drops below diesel emissions by 2030 (1239 tonnes) but remains financially negative (-254 percent); it becomes positive by 2035 (389 percent). Battery emissions fall to 298 tonnes, while gray-hydrogen fuel cells reach 3209 percent return. Values are transcribed in transition-results.csv. The five mechanisms follow the model methods. Scenario factors are five powertrains, three technology paths (constant/middle/advanced), one baseline grid, three vehicle lives (5/10/15 years), three transition years, and two model modes (linear/nonlinear), totaling 270. The 25-year study horizon differs from vehicle life.

A reported-value replot, not a new simulation or execution of the recovered synthetic-data demo. Connected points compare modeled adoption-year scenarios, not longitudinal observations. One deterministic value per scenario; no replicate or uncertainty interpretation. The paper calls grid-electrolysis hydrogen green hydrogen; the figure names the electricity source explicitly. Table 2 values are used consistently rather than reconciling inconsistent prose by inventing values.

Publication links: https://doi.org/10.1142/S0218348X26400633.

## Build and inspect

Requirements: Python 3, TeX/TikZ, Helvetica-compatible fonts, Ghostscript, Poppler
and a sibling research-ops checkout. Quantitative figures additionally require
gnuplot with the cairolatex terminal (tested with gnuplot 6.0.3). `GNUPLOT` can
select a compatible executable.

From the repository root:

```sh
sh figures/abstracts/build.sh
```

The script regenerates the selected SVGs and anti-aliased PNG fallbacks. Generated PDF intermediates, native
gnuplot exports and compiler logs stay in ignored `.local/figures/`; remove that
folder after checking the outputs. The published package retains editable TikZ,
plot scripts/data, required artwork, source evidence and checksums.

Abstracts use a 240 × 180 mm canvas and export at 2400 × 1800 px (4:3), with
960 × 720 px review views during builds. All native labels are 9 pt
Helvetica-compatible. Artwork and native labels remain black on white. PNG fallbacks use anti-aliased
greyscale edges; no one-bit threshold is applied. Original artwork inputs remain intact.
Informational dots, hatches, dash styles and markers encode categories.

Inspect full-size and README-size renders after editing. Check scientific
meaning, units, marker counts, label clearance, padding, legend scope and
bottom-right citations. A faithful replot is not an independent reproduction.
No publisher figures or manuscript PDFs are included, and no new asset reuse
license is asserted. Source data and illustrative content remain distinct.

Both plots share one outer results frame. Their legend and scenario conditions
sit below the individual plot boxes, with matching 2 mm visible side/top padding
and plot gutter. Frame coordinates compensate for differing stroke widths.

## Selected export formats

The project README embeds the anti-aliased PNG with an opaque white background
for visibility in light and dark themes. Clicking the preview opens its SVG. PDF intermediates stay in ignored local storage;
no PDFs are published. Poppler's `pdftocairo` is required for SVG export.

These SVGs contain native vector geometry, plots and glyph outlines with no
embedded bitmap images. Keep the TeX sources for editable labels.

PNG fallbacks: [decarbon-plot](assets/decarbon-plot.png) · [decarbon](assets/decarbon.png)

Outer frames use equal 3 mm page margins on every side, with 4 mm gutters
between main panels/rows. Decarbon shared-result panels use matching 2 mm visible inner padding
and gutters, measured between stroke edges. Artwork proportions and native font sizes are preserved.

The complete plot content, including axis titles, ticks and direct labels, is
centered horizontally in each panel. Marker labels have a visible clearance
from the marker edge; captions/subtitles follow their panel centerline.

Repeated nested cells use equal 3 mm left, right and bottom insets. Their widths
and centers are calculated from the parent bounds; glyph proportions are intact.

Main frames use 1.5 pt borders; nested frames use 1 pt, with square miter joins. Plot axes and illustration
strokes retain their independent weights.

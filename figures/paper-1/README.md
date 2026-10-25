# Paper 1 graphical abstract

Vehicle choice and transition timing are compared through linear and nonlinear
emissions/cost accounting, exposing trade-offs between financial returns and
emissions savings.

Source: Singh, Chang and Karaca, *Fractals* (2026), article 2640063,
[DOI 10.1142/S0218348X26400633](https://doi.org/10.1142/S0218348X26400633).
The figure describes this published study, not the repository's exploratory demo.

## Scientific grounding

- Figure 1, publication p. 7: sources, annual accounting, aggregation and outputs.
- Sections 2.3–2.4, pp. 9–11: cost/ROI accounting and the five nonlinear features.
- Section 3.1, pp. 11–12: five powertrains, three technology assumptions, one grid
  trajectory, three vehicle lifetimes and three transition years; 135 configurations
  evaluated in each of two model modes, giving 270 scenarios.
- Table 1, p. 12, and Figure 7, p. 19: the Mid / 2025 / 10-year comparison.
  BEV lifetime emissions are 820 tonnes CO2e (linear) or 831 tonnes (nonlinear),
  against 2,173 tonnes for matched diesel: about 62% lower in either mode.
- Sections 3.2 and 5: grid-linked green-hydrogen timing and divergence between
  economic returns and emissions reductions. No universal technology winner is implied.

The reported horizon is 25 years; individual vehicle lifetimes are 5, 10 or 15
years. This figure does not equate the horizon with a vehicle lifetime. The
three transition years are 2025, 2030 and 2035. Only the DCCEEW baseline grid is
represented in the original scenario grid. Results are per vehicle, not observed
fleet totals. TCO and ROI retain the publication's definitions; ROI uses its
undiscounted cost comparison, with NPV TCO reported separately in the paper.

## Artwork and limits

All artwork is newly authored native TikZ. The identical trucks are schematic
side views, not drawings of particular models, trial vehicles or validated
hardware. Brackets gather choices/features; arrows indicate model inputs and
output flow. They are not causal estimates or a physical control circuit.

No original publisher figure is copied. There are no invented curves, data points
or new simulation results. The approximate BEV percentage is a reported result
with its scenario identified, not a value computed by the demo package.

The 220 × 110 mm canvas has a 2:1 ratio. The PNG is 2200 × 1100 pixels. All
native labels use 9 pt Helvetica-compatible text. The final rendering is black
linework on white, without grey fills or shading. Both full-size and 900-pixel
review views were inspected for legibility, counts, clipping and arrow endpoints.

## Rebuild

Requirements: Python 3, TeX with TikZ and Helvetica-compatible fonts,
Ghostscript and Poppler. From the repository root, with `research-ops` alongside:

```sh
python3 ../research-ops/.agents/skills/tikz-graphical-abstracts/scripts/render.py \
  figures/paper-1/graphical-abstract.tex \
  --out-dir .local/figure-export --build-dir .local/figure-build
gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pnggray \
  -dTextAlphaBits=4 -dGraphicsAlphaBits=4 -dFIXEDMEDIA -dPDFFitPage \
  -g2200x1100 -r254 \
  -sOutputFile=figures/paper-1/assets/graphical-abstract.png \
  .local/figure-export/graphical-abstract.pdf
pdftocairo -svg .local/figure-export/graphical-abstract.pdf \
  .local/figure-export/graphical-abstract.svg
```

Without the governance checkout, compile the standalone TeX directly with
`pdflatex -no-shell-escape -halt-on-error -output-directory=.local/figure-build figures/paper-1/graphical-abstract.tex`
after creating that build directory, then export with Ghostscript/Poppler. The canonical
editable source is `graphical-abstract.tex`.

Generated PDFs and build products remain under ignored `.local/`. Only the PNG and
native TeX source are published; optional SVG exports stay local. Reference/output hashes and actual
dimensions are recorded in `provenance.json`. No new figure reuse license is
asserted by this companion.

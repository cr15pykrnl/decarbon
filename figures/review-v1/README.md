# Graphical abstract review, version 1

These 4:3 candidates are prepared for owner feedback. The previously selected
figure remains in place. Paper titles/authors/DOIs stay outside the artwork.

## Refined brief

Explain the 270-run scenario design, show how lifecycle emissions and cost are compared, and replot the headline nonlinear results with their conditions.

Use source-supported categories and results, a 240 × 180 mm canvas, 9 pt native
labels and precise black linework. Preserve distinctions between demonstrations,
qualitative observations, simulations and measured outcomes. No paper PDFs are
added to the repository.

## Candidates

- [decarbon](assets/decarbon.png), editable source `decarbon.tex`.

## Source evidence

Table 1, publication p. 12: nonlinear Mid technology, 2025 transition, 10-year vehicle life, DCCEEW baseline grid. Emissions are tonnes CO2e per vehicle; TCO is total undiscounted AUD, displayed in millions rounded to three decimals. Original exact values are in reported-results.csv. One deterministic value per scenario; no error bars or replicated-sample interpretation. Figures 1 and 7 and sections 2.3–3.1 support the method and factorization.

This is a replot of published values, not a run of the simulation or the separate demo code. ROI is recorded for traceability but not plotted. The 25-year horizon is distinct from the 5/10/15-year vehicle lifetimes.

Sources: https://doi.org/10.1142/S0218348X26400633.
Source values, conditions, transformations and input/output hashes are recorded
in `provenance.json` and, where numeric values are replotted, `reported-results.csv`.
Existing reused artwork retains its original resolution and generation provenance
in the selected figure's original source directory.

## Rebuild and review

With TeX, Ghostscript, Poppler and a sibling research-ops checkout, run from the
repository root (replace NAME with a candidate stem above):

```sh
python3 -I ../research-ops/.agents/skills/tikz-graphical-abstracts/scripts/render.py \
  figures/review-v1/NAME.tex --out-dir .local/abstract-review-v1 \
  --build-dir .local/abstract-review-build
```

The current renderer defaults to 2400 × 1800 output and 960 × 720 review for this
physical 4:3 page. PNGs are selected review exports; PDFs and logs stay ignored.
Keep the 4:3 geometry when adjusting individual panels. Re-render and inspect
labels, numeric scales, counts and arrow endpoints after changes. These are
first review compositions, not a claim of venue-specific submission compliance.

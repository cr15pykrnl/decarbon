#!/bin/sh
set -eu
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$repo_root"
mkdir -p .local/figures/export .local/figures/build figures/abstracts/assets
mkdir -p .local/figures/plots
cd .local/figures/plots
"${GNUPLOT:-gnuplot}" ../../../figures/abstracts/decarbon.gp
cd "$repo_root"
python3 -I ../research-ops/.agents/skills/tikz-graphical-abstracts/scripts/render.py \
  figures/abstracts/plot-panel.tex --out-dir .local/figures/export \
  --build-dir .local/figures/build --svg
cp .local/figures/export/plot-panel.png figures/abstracts/assets/decarbon-plot.png
cp .local/figures/export/plot-panel.svg figures/abstracts/assets/decarbon-plot.svg
for name in decarbon; do
  python3 -I ../research-ops/.agents/skills/tikz-graphical-abstracts/scripts/render.py \
    "figures/abstracts/$name.tex" --out-dir .local/figures/export \
    --build-dir .local/figures/build --svg
  cp ".local/figures/export/$name.png" "figures/abstracts/assets/$name.png"
  cp ".local/figures/export/$name.svg" "figures/abstracts/assets/$name.svg"
done

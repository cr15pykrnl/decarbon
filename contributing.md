# Working with Decarbon

Clone the repository and create a Python 3.10+ environment:

```sh
git clone https://github.com/cr15pykrnl/decarbon.git
cd decarbon
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests
```

For exploratory notebooks, install `python -m pip install -e '.[notebooks]'`
and run `jupyter lab`. Both notebooks generate illustrative synthetic scenarios;
they do not reproduce the published simulation or consume the AES tables.
Stored notebook outputs have been cleared; execute cells to produce outputs.
Run all cells in order in the same kernel. Each notebook executes ordered source
files from `examples/`, relative to its location in `notebooks/`.

## Data sources

Government tables are available from the official
[Australian Energy Statistics 2024 release](https://www.energy.gov.au/publications/australian-energy-update-2024)
and its [machine-readable files](https://www.energy.gov.au/publications/australian-energy-statistics-2024-machine-readable-files).
This repository does not mirror them on HF. The exploratory demo does not read
those tables: it generates results from the illustrative parameters in its code.

No paper-specific simulation dataset or trained model has been released here.
If research outputs are released later, keep bulk data on HF with pinned versions,
checksums, clear units and a demonstrated relationship to the published method.

## Maintainer setup

Work directly on `main`. With the shared `research-ops` checkout alongside this
repository, run `python3 ../research-ops/scripts/setup-project.py --repo .`.
This installs the research Git identity and shared hooks. Readers can use the
public code and data without that governance checkout.

Do not add manuscript PDFs, Word drafts, private inventories or bulk data to Git.
Keep the published model distinct from the exploratory demonstration. Record
actual data changes and checks; do not claim reproduced paper results from demos.

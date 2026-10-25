# Decarbon research-ops audit

Self-review, 25 October 2026. Baseline source revision:
`7e6f9f269272bc6495aa3101912501c4f3837a73`.

Scope: published-paper identity, source/data distinctions, Python interfaces,
portable installation, documentation examples, figure fidelity, privacy,
source-size limits, reachable Git history and public release policy. This is
not an independent validation of the paper's results or a full notebook run.

## Open findings

### Medium: default uncertainty configuration is silently ignored

`digital_twin/utils.py:99` returns uncertainty keys that are all absent from
`create_base_scenario()`. `digital_twin/models.py:227–229` silently skips keys
absent from the supplied base parameters. Passing those two public helpers
together produces identical parameter dictionaries across every draw.

```python
from digital_twin.models import monte_carlo_simulation
from digital_twin.utils import create_base_scenario, create_uncertainty_params
draws = monte_carlo_simulation(
    create_base_scenario(), create_uncertainty_params(), 4, random_seed=5,
)
assert all(row == draws[0] for row in draws)
```

Effect: a caller can mistake a deterministic result for an uncertainty analysis.
Reject unknown keys and document explicit mappings between uncertain quantities
and base parameter values. Do not silently choose mappings that change science.

### Medium: zero emissions baseline is reported as a valid percentage

`digital_twin/utils.py:224–225` returns `0.0` for a zero baseline, including
`calculate_co2_reduction_percentage(0, 100)`. Relative percentage change is
undefined in this case. The returned number hides that missing definition and
can be interpreted as no change. Use an explicit error or documented missing
value, and distinguish that policy from the ordinary positive-baseline formula.

### Low: executable documentation has five failures

Using Python 3.12 and NumPy 2.4.6, `doctest.testmod` finds five failures among
15 examples across `digital_twin.models` and `digital_twin.utils`:

- Battery degradation: 235.44198787134206 km, rather than the stated 236.8.
- NPV: −30,218.698887657454, rather than the stated −30,398.26.
- Energy example: correct value, but a NumPy scalar representation differs.
- Break-even example: unrounded 4.411764705882353 rather than 4.41.
- Uncertainty example: Python prints `0.2` rather than the literal `0.20`.

The first two are incorrect documented values; the others need intentional
formatting or numerical assertions. No formula changes were made during this audit.

## Corrected documentation

`AGENTS.md` incorrectly said AES tables were downloaded from HF. It now links
to the official government source, matching the owner's decision and README.
The new graphical abstract has paper-specific source notes, native source,
reviewed PNG export and exact artifact hashes. No manuscript PDF is included.

## Checks and limits

- Four existing numerical contract tests pass. They do not exercise the failures
  above and therefore do not establish complete numerical correctness.
- Editable package installation passed in Python 3.12 with NumPy 2.4.6 during
  preparation of the baseline release; the package configuration is unchanged.
- Python examples and notebook code compile; full notebook analyses and the
  published simulation have not been run. No paper-matched implementation or
  complete reproduction dataset has been identified in this companion.
- README title, authors, DOI, abstract and research scope checked against the
  published paper. The original and demo identities remain distinct.
- Government inputs link to the official AES 2024 source; no public HF mirror.
- The private scientific archive was verified by downloading every original and
  comparing sizes and SHA-256 before working-folder cleanup. Private identifiers
  and path inventories are not part of the public companion.
- Current Git identity, local links, source lengths, privacy, figure exports and
  complete reachable-history release classification are checked for this change.

The companion satisfies the reviewed publication/privacy packaging checks. Its
exploratory numerical API has the open findings above and is not fully compliant
with the shared input-validation and numerical-evidence requirements.

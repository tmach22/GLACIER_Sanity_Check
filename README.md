# GLACIER Sanity Check

Sibling project to [`ICEBERG_Sanity_Check`](https://github.com/tmach22/ICEBERG_Sanity_Check),
set up to eventually benchmark the GLACIER MS/MS spectrum model
(`coleygroup/ms-pred`) against NIST'20 data.

## Status

Repo scaffolding + data are in place; **no GLACIER predictions/benchmarks have
been run yet.**

## What's here

- `vendor/ms-pred` (git submodule, pinned to the same commit as
  `ICEBERG_Sanity_Check`: `0f620ceeee1f0930215282a58e58066a79f88dd0`)
- `vendor/ms-data-parser` (git submodule, same pin: `08ab971714a965c7aa624b2a9aa455ba34edfcc4`)
- `env/ms-pred-uv.lock` + `env/setup_ms_pred_env.sh` — reproduces the exact
  Python environment used in `ICEBERG_Sanity_Check` (see that repo's script
  for the rationale). Run `./env/setup_ms_pred_env.sh` after
  `git submodule update --init --recursive`.
- `vendor/ms-pred/data/spec_datasets/nist20/` — copied directly from
  `ICEBERG_Sanity_Check`'s already-processed NIST'20 data (not tracked by
  git, licensed data, lives only in the submodule's untracked working tree):
  - `labels.tsv`
  - `splits/{split_1,scaffold_1,hyperopt,fingerprint_1}.tsv`
  - `retrieval/cands_df_{split_1,scaffold_1}_50.tsv` (+ pickled versions)
  - `subformulae/no_subform.hdf5`

  Not copied: `spec_files.hdf5` (raw pre-subformula spectra; not needed by
  any inference/eval script we've used so far -- can be copied over later
  if a GLACIER training/preprocessing step turns out to need it) and the
  raw `NIST20_data/` MGF/TSV source files (labels.tsv/no_subform.hdf5 are
  already the processed products of those).

## Important gap: no NIST-licensed GLACIER checkpoint

Unlike ICEBERG, `ms-pred` only publicly provides a GLACIER checkpoint
trained on **MassSpecGym**, not NIST'20/23 -- see the GLACIER section of
`vendor/ms-pred/README.md`. Running that checkpoint against the NIST20 data
above would be an out-of-domain cross-dataset check, not a reproduction of
the numbers reported in the GLACIER paper (which are on MassSpecGym).

Options going forward (not yet decided/started):
1. Run the MassSpecGym-trained checkpoint against this NIST20 data anyway
   (fast, already possible, but not the paper's reported benchmark).
2. Set up the proper MassSpecGym data pipeline to match the paper's actual
   reported numbers.
3. Email the ms-pred maintainer for a NIST-licensed GLACIER checkpoint
   (same contact ICEBERG's NIST weights came from), then reuse this NIST20
   setup exactly like ICEBERG.

## Data governance

Same rule as `ICEBERG_Sanity_Check`: NIST'20 is licensed data. Any file
containing SMILES/spectrum-IDs/peak-intensities derived from it must not be
pushed to GitHub (private repo still counts) without explicit sign-off --
aggregate-only summaries are fine.

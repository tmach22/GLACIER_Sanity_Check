"""convert_glacier_sparse_preds_for_fidelity_eval.py

Bridge GLACIER's predict_smis_joint.py output into the dense-`intens`
PredSpecDB convention analysis/spec_pred_eval.py expects (see
ICEBERG_Sanity_Check's preprocessing/scripts/convert_binned_preds_for_fidelity_eval.py
for the fuller writeup of that read/write contract; this is a sibling
script for GLACIER's different output shape).

Why this differs from ICEBERG's converter: ICEBERG's predict_smis.py
--binned-out writes a *sparse-encoded* dense binned spectrum (has_binned_spec)
that the MassSpec.binned_spec property decodes on read. GLACIER's
predict_smis_joint.py has a --binned-out flag too, but it's dead code --
never wired into the writer -- so its output only ever has sparse top-k
(masses, intens) peaks, same shape as ICEBERG's non-binned mode. This
script bins those sparse peaks itself, using the exact same
common.bin_spectra(..., pool_fn="max") call analysis/spec_pred_eval.py's
process_spec_file() uses for the *true* experimental spectrum, so both
sides of the cosine-similarity comparison are binned identically.

predict_smis_joint.py was run directly against a labels.tsv-shaped subset
containing ONLY the true molecules (no candidate/decoy pool), so -- unlike
the retrieval-mode ICEBERG conversion -- there is no need to filter out
decoys here: every (name, remark, cms) group already is the true molecule.

Usage (run from vendor/ms-pred/, with the ms-pred venv active):
    .venv/bin/python ../../preprocessing/scripts/convert_glacier_sparse_preds_for_fidelity_eval.py \
        --in-h5 results/glacier_nist20/split_1_rnd1/smoke_test_300/preds.hdf5 \
        --out-h5 results/glacier_nist20/split_1_rnd1/smoke_test_300/preds_fidelity_eval.hdf5 \
        --num-bins 15000 --upper-limit 1500
"""
import argparse
import sys
from pathlib import Path

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in-h5", required=True)
    ap.add_argument("--out-h5", required=True)
    ap.add_argument("--num-bins", type=int, default=15000)
    ap.add_argument("--upper-limit", type=int, default=1500)
    ap.add_argument("--ms-pred-root", default=".")
    args = ap.parse_args()

    sys.path.insert(0, str(Path(args.ms_pred_root) / "src"))
    import ms_pred.common as common

    Path(args.out_h5).parent.mkdir(parents=True, exist_ok=True)

    src_db = common.PredSpecDB(h5_path=Path(args.in_h5), mode="r")
    out_db = common.PredSpecDB(
        h5_path=Path(args.out_h5), mode="w", num_h5s=1,
        has_probs=False, has_brokens=False, has_masses=False,
        has_masses_no_adduct=False, has_frag_form_vecs=False,
        has_frags=False, has_intens=True, has_pulled_atoms=False,
        has_binned_spec=False,
    )

    n_groups = 0
    n_written = 0
    for entry in src_db.get_all_specs():
        if len(entry) == 3:
            name, remark, cms = entry
        else:
            name, cms = entry
        n_groups += 1

        bare_name = name[len("pred_"):] if name.startswith("pred_") else name

        for ce_key, mass_spec in cms.items():
            masses = np.asarray(mass_spec.masses, dtype=np.float64)
            intens = np.asarray(mass_spec.intens, dtype=np.float64)
            spec_ar = np.stack([masses, intens], axis=1)
            dense = common.bin_spectra(
                [spec_ar], num_bins=args.num_bins, upper_limit=args.upper_limit, pool_fn="max"
            )[0]

            ce_val = float(mass_spec.collision_energy)
            write_name = f"{bare_name}_collision {ce_val:.0f}"

            out_ms = common.MassSpec(
                root_canonical_smiles=mass_spec.root_canonical_smiles,
                adduct=mass_spec.adduct,
                collision_energy=ce_val,
                intens=np.asarray(dense, dtype=np.float32),
                # remark intentionally omitted -> keeps get_all_specs() 2-tuple form
            )
            out_db.write(write_name, out_ms)
            n_written += 1

        if n_groups % 1000 == 0:
            print(f"  ...{n_groups} groups processed, {n_written} (spec,CE) entries written", flush=True)

    out_db.close()
    print(f"Done. {n_groups} groups -> {n_written} (spec, collision_energy) entries written.")
    print(f"Output: {args.out_h5}")


if __name__ == "__main__":
    main()

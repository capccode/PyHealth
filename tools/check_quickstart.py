#!/usr/bin/env python
"""Run the documented PyHealth 2.0 quickstart pipeline end-to-end.

Mirrors the 5-stage pipeline from ``docs/api/overview.rst`` against the
bundled offline fixture ``test-resources/core/mimic4demo`` so it can run
without network access or credentialed data:

    dataset -> task -> set_task -> dataloader -> model -> trainer

Exits 0 when every stage completes and evaluation returns metrics.
"""

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    from pyhealth.datasets import MIMIC4Dataset, get_dataloader, split_by_patient
    from pyhealth.models import MLP
    from pyhealth.tasks.length_of_stay_prediction import (
        LengthOfStayPredictionMIMIC4,
    )
    from pyhealth.trainer import Trainer

    demo_root = REPO_ROOT / "test-resources" / "core" / "mimic4demo"
    with tempfile.TemporaryDirectory() as cache_dir:
        # Stage 1-2: raw files -> BaseDataset -> Patient/Event
        dataset = MIMIC4Dataset(
            ehr_root=str(demo_root),
            ehr_tables=["diagnoses_icd", "procedures_icd", "prescriptions"],
            cache_dir=cache_dir,
        )
        assert len(dataset.unique_patient_ids) > 0, "no patients loaded"

        # Stage 3: task -> SampleDataset
        samples = dataset.set_task(LengthOfStayPredictionMIMIC4())
        assert len(samples) > 0, "set_task produced no samples"

        # Stage 4: dataloaders
        train_ds, val_ds, test_ds = split_by_patient(samples, [0.6, 0.2, 0.2])
        train_dl = get_dataloader(train_ds, batch_size=8, shuffle=True)
        test_dl = get_dataloader(test_ds, batch_size=8, shuffle=False)

        # Stage 5: model + trainer
        model = MLP(dataset=samples)
        trainer = Trainer(model=model, metrics=["accuracy"], device="cpu")
        trainer.train(train_dataloader=train_dl, epochs=1)
        results = trainer.evaluate(test_dl)
        assert "accuracy" in results, f"unexpected eval output: {results}"
        print(f"Quickstart pipeline OK: {results}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

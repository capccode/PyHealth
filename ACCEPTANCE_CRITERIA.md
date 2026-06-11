# PyHealth 2.0 Hardening — Acceptance Criteria

These criteria were drafted by three independent reviews (test/CI health,
architecture consistency, docs ↔ code alignment) and reconciled into the
machine-checkable list below. `tools/check_acceptance.sh` runs every check
and prints PASS/FAIL per criterion; the hardening pass is complete when it
exits 0.

Run with the environment's interpreter, from the repo root:

```bash
PYTHON=/path/to/venv/bin/python tools/check_acceptance.sh        # full (~10 min)
PYTHON=/path/to/venv/bin/python tools/check_acceptance.sh --fast # skip suites
```

## Criteria

| #   | Criterion | Verified by |
|-----|-----------|-------------|
| C1  | `tests/core` exits 0 — no failures, no errors (skips allowed) | `unittest discover -t . -s tests/core` |
| C2  | Every skip reason is on the documented allowlist (optional deps, CUDA, Hugging Face Hub reachability, fixture limitations) | skip-reason scan of the C1 log |
| C3  | `tests/nlp` exits 0 | `unittest discover -t . -s tests/nlp` |
| C4  | Architecture contracts hold: every `pyhealth` submodule imports cleanly (no import-time env/network requirements) and every concrete `BaseTask` subclass defines `task_name`, `input_schema`, `output_schema` | `tools/check_task_contracts.py` |
| C5  | The documented 5-stage quickstart pipeline (`docs/api/overview.rst`) runs end-to-end on the bundled offline fixture `test-resources/core/mimic4demo`: dataset → task → `set_task` → dataloader → model → `Trainer.train`/`evaluate` | `tools/check_quickstart.py` |
| C6  | All imports shown in the docs quickstarts resolve | inline import check in the script |
| C7  | No stale third-party references in `docs/` (the *combo* library, `yzhao062/*`, `github.com/ycq091044/*` fork links) | grep |
| C8  | Tutorial videos recorded against PyHealth 1.x are labeled "1.x legacy" rather than presented as current | grep |
| C9  | No environment-specific `/srv/local` example paths in `pyhealth/` source or docstrings | grep |
| C10 | `docs/log.rst` development log covers the 2.0 release | grep |

Notes on intentional scope:

- External link liveness and Hugging Face-dependent tests cannot be
  validated in a network-restricted environment. HF-dependent tests are
  guarded by `tests.base.hf_hub_accessible()` so they still run in CI,
  which has internet access.
- `tests.core.test_sdoh.TestSdoh.test_predict` additionally depends on the
  gated `meta-llama/Llama-3.1-8B-Instruct` model; even in CI it passes only
  via its existing gated-repo exemption.

## Architecture audit — findings and disposition

Fixed in this pass:

- `pyhealth/medcode/pretrained_embeddings/lm_emb/openai_retriever.py`
  raised `KeyError: OPENAI_API_KEY` at **import time**; the key is now read
  lazily inside `embedding_retrieve` (C4 enforces this class of bug).
- 49 hardcoded `/srv/local/...` example paths in docstrings and demo blocks
  across `pyhealth/{tasks,datasets,models,calib}` replaced with neutral
  `/path/to/data/...` paths (C9).
- Hugging Face download errors in `tests/core/test_sdoh.py` and
  `tests/core/test_transformer_deid.py` converted to connectivity-guarded
  skips via `tests.base.hf_hub_accessible()` (C1/C2).

Deferred (documented, out of scope for this pass):

- **Function-based 1.x tasks** (`drug_recommendation.py`,
  `cardiology_detect.py`, `sleep_staging.py`, `patient_linkage.py` export
  `*_fn` functions) coexist with class-based `BaseTask` tasks. Migrating
  them is an API change that needs its own deprecation cycle.
- **Generator models** (`pyhealth/models/generators/*`: GPT2, HALO, MedGAN,
  CorGAN) do not return the standard `{"loss", "y_prob", "y_true",
  "logit"}` forward contract; they generate synthetic records instead.
  Deliberate specialization — should be documented in the models API page.
- **`SdohClassifier`** (`pyhealth/models/sdoh.py`) is an LLM-wrapper
  exposing `predict()` only (no `forward()`), so it is not `Trainer`
  compatible. Deliberate; same documentation note applies.
- **Module-role clarity**: `pyhealth/sampler` (single GraphSAGE sampler),
  `pyhealth/tokenizer.py` (1.x utility still used by `tfm_tokenizer`), and
  `pyhealth/nlp` (metrics only) sit outside the documented 5-stage
  pipeline. Candidates for consolidation in a future minor release.

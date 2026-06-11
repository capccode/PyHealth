Frequently Asked Questions
==========================

----


What does PyHealth 2.0 support?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PyHealth 2.0 is a comprehensive healthcare AI toolkit that goes beyond
structured EHR data: it provides a unified API for EHR tables, medical
images, biosignals (EEG/ECG/sleep), clinical text, and genomics. The
:doc:`architecture overview <api/overview>` describes how datasets, tasks,
processors, models, and the trainer fit together.

Highlights of the 2.0 release:

- Native datasets for MIMIC-III/IV, eICU, OMOP-CDM, FHIR, and many
  modality-specific collections (chest X-ray, sleep staging, EEG, ECG).
- A 5-stage pipeline (dataset → task → processors → model → trainer) with
  caching and dynamic scaling from laptop to cluster.
- Post-hoc model calibration (``pyhealth.calib``) and interpretability
  (``pyhealth.interpret``) that plug into any trained model.

For the roadmap and ways to get involved, see :doc:`how_to_contribute`
and the `open issues <https://github.com/sunlabuiuc/PyHealth/issues>`_.


Inclusion Criteria
^^^^^^^^^^^^^^^^^^

Similarly to scikit-learn, we mainly consider well-established algorithms
for inclusion. A rule of thumb is at least two years since publication,
50+ citations, and usefulness.

However, we encourage the author(s) of newly proposed models to share and
add your implementation into PyHealth for boosting ML accessibility and
reproducibility. This exception only applies if you could commit to the
maintenance of your model for at least a two-year period.

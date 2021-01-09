### Heart Rate Monitoring in Sports

## Fieldwiz C
Code for the embedded implementation

## FieldWiz Dataset


## FieldWiz Python

* Kubios artefact correction method

Evaluation of the correction method by Kubios
![plot](kubios%20HRV.png)

<u>Under resting conditions</u>:
Beats classified as short/long are corrected by interpolation.
False positives/negatives are correctly corrected and interpolated
Reduced number of ectopic beats

Robust method for artifact correction under rest conditions.

<u>Under running conditions</u>:
False positive ectopic beats, when applied in high heart rate conditions.
Not robust distinction between ectopic and missed beats. Missed beats, wrongly classified as actopic beats, are interpolated instead of being removed.


* Signal Quality index

Evaluating ECG from the different shirts and different conditions (water, no water and electrode gel)

Zhao Z, Zhang Y. SQI quality evaluation mechanism of single-lead ECG signal based on simple heuristic fusion and fuzzy comprehensive evaluation. Front Physiol. 2018;9(JUN):1–13.

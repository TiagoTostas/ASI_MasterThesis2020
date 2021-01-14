### ASI - Heart Rate Monitoring in Sports

## FieldWiz Info
Miscellaneous information about ASI - Advanced Sports Instruments. Videos/News/Reports.

## FieldWiz Dataset
These acquisitions can be used for further evaluation of the ECG signal quality with different acquisition settings: 1) Fieldwiz + Belt; 2) FieldWiz + Shirt Version 1; 3) FieldWiz + Shirt Version 2 and 4) Admos Live.
The metadata relevant to each recording can be found in the header file.

These can be further be used for evaluation of additional algorithms or validate the results of this thesis.

* Activities:

40 recordings acquired using a combination of FieldWiz + Belt or Connected shirt Version 1/2.

* Annotations_Joana:

Annotated: 10 ECG recordings with annotated R-peaks by a cardiopneumologist technician

Engzee_annotated: 10 ECG recordings annotated using the method by Engzee

* Experiments:

Various experiments with electrodes in different configurations, e.g. hand

* HRV_5min

16 recordings acquired during rest using the FieldWiz + Belt or connected Shirt Version 2

## FieldWiz Matlab
* <u>Database Comparison</u>

The proposed R-peak detector was benchamrked in the common Physionet databases: Challenge 2014, MIT_BIH, Noise and Stress database and ST-T.
The databases and the scripts used for benchmarking can be found here.

* <u>Matlab Server</u>

Scripts implemented in the Matlab Server:

ASI-Segmenter: proposed method for R-peak detection.

HR_session: compute basic HR and RR-intervals sequence from the R-peak positions of a single session.

HRV_2min: computation of basic Time and Frequency domain metrics (hrmean, sdnn, rmssd, lnrmssd, rr_intervals, LF, HF, LFHF) using a 2 minute window.

HRV_realtimesession: computation of HR and RMSSD for real-time applications (as implemented for example in Zephyr)

## FieldWiz Python
* <u>R-peak Detectors Comparison</u>

Comparison of temporal precision of different R-peak detectors

* <u>HRV comparison </u>

Study of the influence of different artefact correction techniques in RR-intervals

* <u>Detectors Comparison (N=5 and N=10)</u>

Statistical analysis of the Accuracy, Sensitivity (Se) and Positive Predictive Value (PPV) of the different QRS algorithms evaluated: Pan and Tompkins, Christov, Gamboa, Engelse(modified), Elgendi, Kalidas and proposed method.


* <u>Kubios artefact correction method</u>

Evaluation of the correction method by Kubios2019
![plot](kubios%20HRV.png)

<u>Under resting conditions</u>:
Beats classified as short/long are corrected by interpolation.
False positives/negatives are correctly corrected and interpolated
Reduced number of ectopic beats

Robust method for artifact correction under rest conditions.

<u>Under running conditions</u>:
False positive ectopic beats, when applied in high heart rate conditions.
Not robust distinction between ectopic and missed beats. Missed beats, wrongly classified as actopic beats, are interpolated instead of being removed.


* <u>Signal Quality index</u>

Evaluating ECG from the different shirts and different conditions (water, no water and electrode gel)

Zhao Z, Zhang Y. SQI quality evaluation mechanism of single-lead ECG signal based on simple heuristic fusion and fuzzy comprehensive evaluation. Front Physiol. 2018;9(JUN):1–13.

## Fieldwiz C
Code for the embedded implementation used in the microcontroller

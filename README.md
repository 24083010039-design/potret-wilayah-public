# Potret Wilayah — Public Dashboard

Potret Wilayah is an independent research dashboard for aggregated village/urban classification findings in Kepulauan Bangka Belitung. It is not an official BPS publication and does not imply institutional endorsement.

## Run

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

## Contents and interpretation

- The package includes 393-unit regional summaries, 12 selected public comparisons, 34 indicator metadata records, seven administrative map geometries, and approved aggregate model-evaluation results.
- It contains no village-level microdata, individual predictions, credentials, internal-only aggregate previews, or local research-file loaders.
- Percentages refer to villages/kelurahan in the indicated group, not residents. Model results are cross-validation summaries and repeated out-of-fold counts; they are not forecasts or a replacement for the official classification.
- BIG administrative geometry is simplified for visualization and is not a legal boundary product. BPS logo, research output, geometry, metadata, and model-result publication were authorized for this release.
- Definitions that are research-derived are labeled as such; the interface does not claim formal item-by-item BPS definition verification.
- Plus Jakarta Sans is distributed under SIL Open Font License 1.1; see `assets/fonts/OFL.txt`.

## Data and source acknowledgments

Research data and classification sources are described in the application’s Methods page. The seven-region map uses BIG/RBI administrative geometry as identified in the dashboard. Values are aggregates only.

<!-- @format -->

# Froestry

Froestry is a collection of data processing, analysis, and web visualization tools focused on urban tree scoring, mapping, and heat/impact modelling. The repository contains scripts for data ingestion, processing, scoring, visualization, and a web frontend for maps and dashboards.

**Project Overview**

- **Purpose:**: Tools to process tree/location data, compute heat/impact scores, produce maps, and export web-ready visualizations.
- **Languages:**: Primarily Python (data processing, analysis) and JavaScript (web frontend under `web/`).
- **Key folders:**: See `Repository Layout` for details.

**Repository Layout**

- **`data/`**: Raw inputs, processed outputs and derived files.
  - **`data/raw/`**: Original input files.
  - **`data/processed/`**: GeoJSON and cleaned data used by processing and web export.
  - **`data/outputs/`**: CSV outputs and exported location lists.
- **`scripts/`**: Standalone Python scripts for data processing and analysis (e.g., `run_scoring.py`, `find_nearest_locations.py`, `create_fresh_data_locations.py`).
- **`src/`**: Reusable Python package code (loaders, processors, utils, visualization helpers).
- **`notebooks/`**: Exploratory notebooks.
- **`web/`**: Frontend assets (Vite project, `package.json`) and generated HTML map pages.
- **`tests/`**: Unit tests (if present) to validate functionality.

**Quick Setup**

- **Python environment:** Create a virtual environment and install dependencies using `requirements.txt`.

```bash
# macOS / zsh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- **Frontend (web):** The `web/` folder contains the frontend package. To run or build the web UI:

```bash
cd web
npm install
# for local dev (Vite):
npm run dev
# to build production assets:
npm run build
```

**Common Tasks & Example Commands**

- **Run a processing script**: (example: scoring)

```bash
# from repo root
source .venv/bin/activate
python scripts/run_scoring.py
```

- **Find nearest locations**:

```bash
python scripts/find_nearest_locations.py --input data/raw/somefile.geojson --output data/outputs/nearest_5_locations.csv
```

- **Export processed geojsons and web layers**:

```bash
python scripts/export_all_locations_geojson.py
python scripts/export_fresh_to_web.py
```

- **Open generated maps**: Generated HTML files are under `web/` (e.g., `web/complete_map.html`, `web/fresh_data_map.html`) and can be served as static files or viewed locally by opening the HTML in a browser.

**Data Notes**

- Processed geojsons and exclusion zones live in `data/processed/` (e.g., `exclusion_combined.geojson`).
- Outputs and derived CSVs are stored in `data/outputs/` (e.g., `nearest_5_locations.csv`, `top_100_tree_locations.csv`).
- Large raw datasets are not included — ensure you have the appropriate source files in `data/raw/` before running scripts.

**Testing**

- If tests exist, run them with `pytest`:

```bash
source .venv/bin/activate
pytest -q
```

**Development Tips**

- Keep `requirements.txt` updated after adding new Python dependencies.
- Use `src/` for reusable code; prefer adding unit tests in `tests/` when modifying logic.
- When updating the web frontend, run `npm run build` to produce optimized assets for `web/`.

**Contributing**

- Fork and create a branch for changes.
- Run existing tests and add tests for new logic.
- Submit a pull request with a clear description of changes.

**License**

- No license file detected in the repository. Add a `LICENSE` file if you want to clarify reuse and distribution terms.

**Contact / Maintainer**

- Maintainer: Shaharyar Nawaz (repository owner)
- For questions or feature requests, open an issue in the repository.

**Next Steps**

- Consider adding a `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and a `LICENSE`.
- Add CI (GitHub Actions) to run `pytest` and linting on PRs.

---

Generated README for the Froestry project. If you want, I can:

- Expand sections with specific examples for individual scripts, or
- Add `CONTRIBUTING.md` and a simple GitHub Actions CI workflow.

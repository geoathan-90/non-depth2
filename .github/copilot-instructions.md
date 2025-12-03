# Copilot instructions for this repo

This project is a small Python-based structural calculation toolkit. Keep changes minimal and follow the project-specific conventions below.

- **Primary files**: `main.py` (entrypoint, calculation flow), `helpers.py` (small math helpers + CSV-driven lookup tables). Data CSVs live in the repo root: `fortia_pyrgon.csv`, `oplismoi_plakas.csv`, `oplismoi_styliskou.csv`, `kh_table.csv`.
- **How to run**: use the interpreter in the dev container; install runtime deps and run directly:
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install pandas numpy`
  - `python main.py` or `python helpers.py`

- **Big picture / data flow**:
  - `main.py` reads `fortia_pyrgon.csv` into `loads` and selects a column by tower name (e.g. `Tower = "T5"`). It uses helper functions from `helpers.py` (`volume`, `weight`) to compute volumes and weights and then prints several scalar results.
  - `helpers.py` reads `oplismoi_plakas.csv` and extracts many lookup arrays via positional indexing (`iloc[:, index]`). Those arrays are used as bins/labels for categorization elsewhere.

- **Important conventions & gotchas**:
  - CSVs are parsed by positional column indices (e.g. `plaka.iloc[:, 2]`, `plaka.iloc[:, 3]` etc.). Do not reorder columns or switch to name-based access without updating all `iloc` usages.
  - Units are encoded in comments (Greek). `volume(side, height)` returns m^3, `weight(density, volume)` returns kg. Keep units consistent when editing constants in `main.py` (densities are kg/m3, lengths in meters, loads in kN then multiplied by 1000 to become N/kg depending on context).
  - Many variable names and comments are in Greek; preserve these where practical. When adding new variables, add an English inline comment to help future maintainers.
  - `__main__` sections print results; there is no test harness. Any automated changes should preserve printed outputs and numeric formatting unless explicitly improving UX.

- **Typical small edits an agent may be asked to do**:
  - Change the active `Tower` by editing `Tower = "T5"` in `main.py` to another column name present in `fortia_pyrgon.csv`.
  - Adjust densities or geometry constants in `main.py` (e.g. `concrete_density`, `A`, `C1`) — verify units in comments before changing.
  - If you need to change lookups in `helpers.py`, update both the `bins` and `labels` lines together and add a short comment explaining which CSV column index changed.

- **When modifying CSV handling**:
  - Prefer adding explicit header-aware parsing only after verifying every `iloc` reference. Example migration step: add `plaka = pd.read_csv('oplismoi_plakas.csv', header=0)` and then replace positional `iloc` with `plaka['ColumnName']` across both `helpers.py` and all callers.

- **Dependencies & environment**:
  - This project only requires `pandas` and `numpy`. No tests or packaging are present.

- **Style & safety**:
  - Keep changes minimal and focused. Preserve Greek comments and original calculation order. If a change affects numeric output, include a short note explaining the rationale and a manual verification command (e.g., `python main.py` and expected sample output).

- **Files to inspect when troubleshooting**:
  - `main.py` — calculation flow, constants, prints
  - `helpers.py` — small functions, CSV-driven lookup arrays
  - `fortia_pyrgon.csv`, `oplismoi_plakas.csv` — data shapes and column ordering

If any of these sections are unclear or you want more detail (for example, a suggested `requirements.txt` or a small unit test harness), tell me what you'd like and I'll update this file.

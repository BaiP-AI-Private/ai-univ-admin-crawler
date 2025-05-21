# Scripts

## Generate List of Universities in the UK

_Script Name:_ generate_uk_univ_csv.py

_Description_:
Scrapes:
  1. The first "wikitable sortable" of UK universities.
  2. The "Member institutions of the University of London" list.
  3. The "Other recognised bodies" list.
Resolves each to its official website & validated admissions page.
Emits: uk_institutions.csv (Name, AdminURL, Country)

If the detected admissions URL returns a non-200 status, the AdminURL field will fallback to the university's main site.

_How to run_:

```
pip install requests beautifulsoup4
python3 generate_uk_institutions_csv.py
```

_Output file_: uk_institutions.csv


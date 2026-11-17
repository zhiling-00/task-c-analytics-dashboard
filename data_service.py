"""Validated, notebook-derived summary data for the Task C presentation app.

Only uses exported/saved results; it does not retrain models or invent row-level data.
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'


def load_csv(name: str) -> pd.DataFrame:
    path = DATA / name
    if not path.is_file():
        raise FileNotFoundError(f'Missing {path}. Keep data/ next to app.py.')
    return pd.read_csv(path)


META = json.loads((DATA / 'metadata.json').read_text(encoding='utf-8'))
A = META['a']
B = META['b']
JOBS = load_csv('a_jobs.csv')
MONTHS = load_csv('a_monthly.csv')
CONTACT = load_csv('a_prior_contacts.csv')
PCA_VARIANCE = load_csv('a_pca_variance.csv')
PCA_LOADINGS = load_csv('a_pca_loadings.csv').rename(columns={'PC':'feature'})
CLUSTER_METRICS = load_csv('a_cluster_selection.csv')
CLUSTER_COUNTS = load_csv('a_cluster_counts.csv')
CLUSTER_PROFILES = load_csv('a_cluster_profiles.csv')
TOPIC_SELECTION = load_csv('b_topic_selection.csv')
TOPIC_SUMMARY = load_csv('b_topic_summary.csv').sort_values('topic_id').reset_index(drop=True)
TEXT_AUDIT = load_csv('b_cleaning_audit.csv')
REPRESENTATIVES = load_csv('b_representative_excerpts.csv')
COMPOSITIONS = {
    col: load_csv(f'a_cluster_{col}_composition.csv').rename(columns={col:'cluster'})
    for col in ('job', 'education', 'marital', 'contact', 'poutcome')
}

MONTH_ORDER = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
MONTHS['month'] = pd.Categorical(MONTHS['month'], categories=MONTH_ORDER, ordered=True)
MONTHS = MONTHS.sort_values('month').reset_index(drop=True)

# Basic integrity checks: avoid presenting inconsistent/mislabeled summaries.
assert CLUSTER_COUNTS['records'].sum() == A['records']
assert len(TOPIC_SUMMARY) == B['topics']
assert int(TOPIC_SUMMARY['dominant_documents'].sum()) == B['usable_docs']
assert abs(TOPIC_SUMMARY['dominant_share'].sum() - 1) < .01
assert {'PC1','PC2'}.issubset(PCA_LOADINGS.columns)
assert len(MONTHS) >= 3


def pct(value: float, digits: int = 1) -> str:
    return f'{value * 100:.{digits}f}%'


def comma(value: int) -> str:
    return f'{int(value):,}'

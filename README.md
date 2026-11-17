# Task C — Analytica: Plotly Dash Analytical Application

A **multi-page interactive Python website** presenting the saved results of:

- **Task A:** UCI Bank Marketing (41,188 observations) — EDA, PCA and K-Means clustering.
- **Task B:** 20 Newsgroups (17,700 usable documents for NMF) — text preprocessing, TF-IDF and 12 NMF topics.

The app **does not re-run PCA, K-Means or NMF**. It reads tables and figures extracted from the final uploaded notebooks, making it quick to demonstrate and deploy.

## Application pages

| Page | Key analytical content | Interactivity |
| --- | --- | --- |
| Overview | Outcome KPIs, cluster subscription, dominant NMF topics | Plotly zoom/hover |
| Bank Marketing | Monthly response rates, occupation distribution, contact-history summary | Change monthly measure and occupation count |
| PCA Analysis | Explained variance, individual PC loadings, saved scatter plot | Select PC1–PC8 for signed loading chart |
| Customer Clusters | K selection, cluster sizes, original-scale profiles, categorical compositions | Choose cluster metric and categorical variable |
| Text Preparation & NMF | Cleaning audit, topic-count comparisons, TF-IDF context | Change topic-count selection metric |
| Topic Explorer | Topic prevalence, keywords, representative excerpts, original category comparison | Choose topic, change prevalence measure, download CSV |
| Methodology & Sources | Dataset links, model pipeline, platform justification, limitations | Source links |

## Easiest way to run locally (Windows / Anaconda)

1. Extract the ZIP file into a folder, for example `C:\Task_C_Analytics_Dashboard`.
2. Open **Anaconda Prompt** or PowerShell in that folder.
3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Start the application:

   ```powershell
   python app.py
   ```

5. Open **http://127.0.0.1:8050** in a web browser. Keep the command prompt running while presenting.
6. Press **Ctrl+C** in the terminal to stop it.

To run it from Anaconda Jupyter's environment, use the Python interpreter associated with your notebook environment.

## Run 100% online (no local Python installation)

Option A: **GitHub + Render** (the code runs in Render's cloud).

1. Sign into [GitHub](https://github.com/) in your browser and create a new repository, for example `task-c-analytics-dashboard`.
2. Upload the **contents of this folder**, including `app.py`, `data_service.py`, `assets/`, `data/`, `requirements.txt` and `Procfile`. Files must remain in the same relative folders.
3. Sign into [Render](https://render.com/), create a new **Web Service**, and connect the GitHub repository.
4. Choose a Python environment/runtime. Use these settings:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:server --bind 0.0.0.0:$PORT`
5. Deploy and open the website URL provided by Render.

Hosting plans, billing, sleep policies, and available options may change; check your provider account before deploying. No online host can run an app unless you upload the source files there. **This ZIP does not create or publish a live URL automatically.**

Option B: **Plotly Cloud** (the Dash provider's own platform) — follow [Plotly's publishing guide](https://dash.plotly.com/), upload your app and dependencies, and use its publication workflow. Account/plan eligibility may vary. Keep `data/` and `assets/` together with `app.py`.

## Folder contents

```
Task_C_Analytics_Dashboard/
├── app.py                       # Dash layouts, pages, charts and callbacks
├── data_service.py              # Read & validate summary data from notebooks
├── requirements.txt             # Python packages
├── Procfile                     # Cloud start command
├── README.md                    # This guide
├── assets/
│   ├── styles.css               # Responsive visual design
│   └── figures/                 # Original notebook plots (PNG)
└── data/
    ├── metadata.json            # Dataset and experiment counts
    ├── a_*.csv                  # Task A aggregate results
    └── b_*.csv                  # Task B aggregate results
```

## Important interpretation note

- The Task A notebook treats `previous > 0` (5,625 records) differently from `pdays != 999` (1,515 records). The dashboard preserves the distinction.
- Task A's **subscription** was not used to fit K-Means; it is a post-hoc outcome comparison.
- Task B's **original 20 categories** were not used to train NMF; the final model identifies 12 independent latent themes.
- The 12 NMF topic labels are interpretations of keywords and representative text, not verified categories.
- The saved notebooks include **aggregate tables and visual output**, not the complete `bank_marketing_clustered.csv` or `newsgroups_nmf_topic_assignments.csv`. Therefore, the app's interactive charts use exact saved aggregates, while PCA scatter and NMF term-weight images are shown as faithful saved figures. Row-level individual/customer filtering is **not** advertised without raw data.
- This demonstration contains excerpts saved in the original notebook and does not need a separate source-dataset download.

## Why Plotly Dash is appropriate for Task C (for your Word report)

> Plotly Dash was selected because it supports a custom multi-page analytical web application using Python, the language used for Tasks A and B. The application combines summary indicators, responsive interactive charts, selectors, topic descriptions, and downloadable tabular results in a consistent interface. It reuses validated notebook outputs instead of retraining computationally intensive PCA, K-Means and NMF models, ensuring the displayed figures are consistent with the submitted analysis. The separated pages distinguish structured-data exploration, dimensionality reduction, segmentation and text analytics, meeting the assignment's requirement for clear presentation and effective visual/interactive elements.

## Recommended demonstration sequence (2–4 minutes)

1. **Overview:** show the two datasets and four summary indicators.
2. **Bank Marketing:** select monthly rate vs volume and change the job count; explain the low overall subscription rate.
3. **PCA Analysis:** inspect the 90% cutoff and choose PC1 vs PC2 loadings.
4. **Customer Clusters:** compare two clusters by `euribor3m`, `previous`, and subscription rate; show the categorical composition selector.
5. **Text Preparation:** show NMF K evaluation across 2–20.
6. **Topic Explorer:** select Automotive, Encryption and Politics topics; show keywords and excerpts; change topic prevalence metric; download the summary.
7. **Methodology:** explain why Dash is suitable and how saved results are used.

## Validation

- Notebook-derived CSV tables were checked for consistency (cluster counts sum to 41,188; NMF dominant topic assignments sum to 17,700).
- Application source Python files were syntax-checked and chart functions validated against saved data.
- **A complete live Dash server test was not performed inside the creation environment**, because the Dash package was not available there. Install `requirements.txt` in a Python-enabled local or online runtime and run `python app.py` to test the full browser experience.

## Data sources

- [UCI Bank Marketing dataset](https://archive.ics.uci.edu/dataset/222/bank+marketing)
- [20 Newsgroups, scikit-learn](https://scikit-learn.org/stable/datasets/real_world.html#the-20-newsgroups-text-dataset)
- [Dash documentation](https://dash.plotly.com/)

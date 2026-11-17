"""Task C — interactive analytical dashboard.

Run: python app.py
Open: http://127.0.0.1:8050
Deploy: gunicorn app:server --bind 0.0.0.0:$PORT

Uses saved results from Task A and Task B notebooks; does not retrain models.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, no_update
from data_service import (
    A, B, META, JOBS, MONTHS, CONTACT, PCA_VARIANCE, PCA_LOADINGS,
    CLUSTER_METRICS, CLUSTER_COUNTS, CLUSTER_PROFILES, COMPOSITIONS,
    TOPIC_SELECTION, TOPIC_SUMMARY, TEXT_AUDIT, REPRESENTATIVES,
    pct, comma,
)

app = Dash(__name__, title='Analytica | Task C Dashboard',
           suppress_callback_exceptions=True,
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])
server = app.server
BLUE = '#3675d2'
TEAL = '#12a591'
NAVY = '#173451'
MUTED = '#7d8da0'
GOLD = '#e4ae55'
COLORS = [BLUE, TEAL, '#e5ac59', '#886ec8', '#4cb6c7', '#ca7292', '#67849d']


def base_figure(height=330):
    fig = go.Figure()
    fig.update_layout(
        template='plotly_white', height=height, margin=dict(l=24, r=18, t=30, b=35),
        font=dict(family="Inter, Segoe UI, Arial", color='#34506c', size=12),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#edf1f6', zeroline=False, linecolor='#e5ebf2'),
        yaxis=dict(gridcolor='#edf1f6', zeroline=False, linecolor='#e5ebf2'),
        hoverlabel=dict(bgcolor='white', font_size=12),
    )
    return fig


def graph(fig=None, *, id=None, height=330):
    # In Dash 4.x, do not pass id=None: omit the property for static charts.
    # Charts updated by callbacks retain their explicit string IDs.
    props = {
        'figure': fig if fig is not None else base_figure(height),
        'config': {'displaylogo': False, 'responsive': True, 'scrollZoom': True},
        'style': {'width': '100%', 'height': f'{height}px'},
    }
    if id is not None:
        props['id'] = id
    return dcc.Graph(**props)


def panel(title, content, subtitle=None, *, extra_class='', footnote=None):
    children = [html.H3(title, className='card-title')]
    if subtitle: children.append(html.P(subtitle, className='card-subtitle'))
    if isinstance(content, list): children.extend(content)
    else: children.append(content)
    if footnote: children.append(html.P(footnote, className='figure-note'))
    return html.Div(children, className=('card ' + extra_class).strip())


def stat(label, value, foot, color='teal'):
    return html.Div([
        html.Div(className='metric-accent' + (' ' + color if color!='teal' else '')),
        html.Div(label, className='metric-label'),
        html.Div(str(value), className='metric-number'),
        html.Div(foot, className='metric-foot'),
    ], className='card')


def heading(kicker, title, description):
    return html.Div([
        html.Div(kicker, className='eyebrow'),
        html.H1(title, className='page-title'),
        html.P(description, className='page-description'),
    ])


def select(id, options, value, label):
    return html.Div([
        html.Label(label, className='filter-label'),
        dcc.Dropdown(id=id, options=options, value=value, clearable=False,
                     className='dash-dropdown', searchable=False),
    ], className='filter-group')


def image(name, caption=None):
    return html.Div([
        html.Img(src=app.get_asset_url(f'figures/{name}'), className='card-media',
                 alt=caption or name),
        html.P(caption or 'Saved figure from the submitted notebook.', className='figure-note'),
    ])


def page(children):
    return html.Div(children, className='page')


def callout(text, title=None):
    return html.Div([
        html.Strong(title + '  ') if title else None,
        text
    ], className='callout')


def fig_subscription():
    fig = base_figure(320)
    fig.add_trace(go.Pie(labels=['Subscribed', 'Not subscribed'],
                         values=[A['subscribed'], A['non_subscribed']], hole=.74,
                         marker=dict(colors=[TEAL, '#dfe8f2']), sort=False,
                         textinfo='percent', hovertemplate='%{label}: %{value:,} (%{percent})<extra></extra>'))
    fig.add_annotation(x=.5,y=.5,text=f"<b>{pct(A['subscribed']/A['records'],2)}</b><br><span style='font-size:11px'>converted</span>",
                       showarrow=False, font=dict(size=22,color=NAVY))
    fig.update_layout(showlegend=True, legend=dict(orientation='h',y=-.11,x=.15), margin=dict(l=5,r=5,t=4,b=42))
    return fig


def fig_cluster_rates():
    df=CLUSTER_PROFILES.sort_values('cluster')
    fig=base_figure(320)
    fig.add_bar(x=[f'Cluster {i}' for i in df['cluster']], y=df['subscribed']*100,
                marker_color=[BLUE,TEAL][:len(df)],
                text=[f'{x:.1%}' for x in df['subscribed']], textposition='outside',
                hovertemplate='%{x}<br>Subscription rate %{y:.1f}%<extra></extra>')
    fig.update_yaxes(title='Subscription rate (%)', range=[0,float(df['subscribed'].max()*115)])
    fig.update_xaxes(title=None)
    return fig


def fig_topic_prevalence(metric='dominant_share'):
    x=TOPIC_SUMMARY.sort_values(metric,ascending=True)
    fig=base_figure(470)
    vals=x[metric]*100 if metric!='dominant_documents' else x[metric]
    fig.add_bar(x=vals,y=x['label'],orientation='h',marker_color=TEAL,
                hovertemplate='%{y}<br>%{x:.2f}'+(' documents' if metric=='dominant_documents' else '%')+'<extra></extra>')
    fig.update_xaxes(title='Documents' if metric=='dominant_documents' else 'Share (%)')
    fig.update_layout(margin=dict(l=15,r=14,t=10,b=35),yaxis=dict(tickfont=dict(size=10)))
    return fig


def fig_month(metric='subscription_rate'):
    df=MONTHS.copy()
    x=df['month'].astype(str).str.title()
    y=df[metric]*100 if metric=='subscription_rate' else df[metric]
    fig=base_figure(330)
    fig.add_bar(x=x,y=y, marker_color=BLUE, marker_line_width=0,
                customdata=df['records'],
                hovertemplate='<b>%{x}</b><br>'+ ('Rate %{y:.2f}%' if metric=='subscription_rate' else 'Contacts %{y:,}') + '<extra></extra>')
    fig.update_yaxes(title='Subscription rate (%)' if metric=='subscription_rate' else 'Observations')
    fig.update_xaxes(title='Campaign month')
    return fig


def fig_jobs(count=10):
    df=JOBS.head(int(count)).sort_values('records')
    fig=base_figure(340)
    fig.add_bar(x=df.records,y=df.job,orientation='h',marker_color=TEAL,
                hovertemplate='%{y}: %{x:,} records<extra></extra>')
    fig.update_xaxes(title='Records')
    fig.update_layout(margin=dict(l=24,r=12,t=12,b=40))
    return fig


def fig_pca_variance():
    fig=base_figure(340)
    df=PCA_VARIANCE
    fig.add_bar(x=df['PC'],y=df['explained_variance_ratio']*100,name='Individual',marker_color=BLUE,
                hovertemplate='%{x}: %{y:.2f}%<extra></extra>')
    fig.add_scatter(x=df['PC'],y=df['cumulative_explained_variance']*100,mode='lines+markers',
                    name='Cumulative',line=dict(color=TEAL,width=3),marker=dict(size=8),
                    hovertemplate='%{x}: %{y:.2f}% cumulative<extra></extra>')
    fig.add_hline(y=90,line_dash='dash',line_color=GOLD,annotation_text='90% retention target',
                  annotation_position='top left')
    fig.update_yaxes(title='Explained variance (%)',range=[0,110])
    fig.update_layout(legend=dict(orientation='h',y=-.28,x=.15),margin=dict(l=22,r=15,t=24,b=57))
    return fig


def fig_pc_loading(pc='PC1'):
    values=PCA_LOADINGS[['feature',pc]].sort_values(pc)
    fig=base_figure(350)
    fig.add_bar(x=values[pc],y=values.feature,orientation='h',
                marker_color=[TEAL if x>=0 else BLUE for x in values[pc]],
                hovertemplate='%{y}: %{x:.3f}<extra></extra>')
    fig.add_vline(x=0,line_color='#9bb0c5',line_width=1)
    fig.update_xaxes(title=f'{pc} component loading')
    fig.update_layout(margin=dict(l=25,r=15,t=15,b=34))
    return fig


def fig_cluster_metric(metric):
    df=CLUSTER_PROFILES.sort_values('cluster')
    y=df[metric] * 100 if metric in ['subscribed','previously_contacted','share'] else df[metric]
    fig=base_figure(345)
    fig.add_bar(x=[f'Cluster {c}' for c in df.cluster], y=y,
                marker_color=[BLUE,TEAL][:len(df)],
                text=[f'{v:.1f}%' if metric in ['subscribed','previously_contacted','share'] else f'{v:,.2f}' for v in y],
                textposition='outside',
                hovertemplate='%{x}: %{y:.2f}' + ('%' if metric in ['subscribed','previously_contacted','share'] else '')+'<extra></extra>')
    fig.update_yaxes(title=('Rate / share (%)' if metric in ['subscribed','previously_contacted','share'] else metric),
                     range=[min(0, float(y.min())*1.2) if float(y.min())<0 else 0,
                            max(0.01, float(y.max())*1.22)])
    return fig


def fig_composition(categorical):
    frame=COMPOSITIONS[categorical].copy().set_index('cluster')
    fig=base_figure(370)
    for i,cat in enumerate(frame.columns):
        fig.add_bar(name=str(cat),x=[f'Cluster {c}' for c in frame.index],y=frame[cat]*100,
                    marker_color=COLORS[i%len(COLORS)],
                    hovertemplate=f'{cat}<br>%{{x}}: %{{y:.1f}}%<extra></extra>')
    fig.update_layout(barmode='stack',legend=dict(orientation='h',y=-.26,x=0,font=dict(size=10)),
                      margin=dict(l=30,r=10,t=12,b=90))
    fig.update_yaxes(title='Within-cluster composition (%)',range=[0,101])
    return fig


def fig_topic_selection(metric='topic_separation'):
    df=TOPIC_SELECTION
    fig=base_figure(355)
    fig.add_scatter(x=df.k,y=df[metric], mode='lines+markers', name=metric,
                    line=dict(color=BLUE,width=2.5),marker=dict(size=7),
                    hovertemplate='K=%{x}<br>%{y:.4f}<extra></extra>')
    chosen=df.loc[df.k==B['topics']]
    if len(chosen):
        fig.add_scatter(x=chosen.k,y=chosen[metric],mode='markers',name='Selected K',
                        marker=dict(size=16,color=TEAL,line=dict(color='white',width=2)),
                        hovertemplate='Selected K=%{x}<br>%{y:.4f}<extra></extra>')
    fig.update_layout(legend=dict(orientation='h',y=-.28))
    fig.update_xaxes(title='Number of topics K',dtick=2)
    fig.update_yaxes(title=metric.replace('_',' ').title())
    return fig


def overview_page():
    return page([
        heading('Coursework · analytical application','An integrated view of structured and text analytics',
                'Explore customer behaviour, PCA-based segments, and themes discovered from public newsgroup discussions. All charts use saved outputs from the submitted notebooks.'),
        html.Div([
            stat('Bank observations',comma(A['records']),'UCI Bank Marketing · complete dataset','blue'),
            stat('Subscription rate',pct(A['subscribed']/A['records'],2),'4,640 successful subscriptions'),
            stat('NMF documents',comma(B['usable_docs']),'Usable posts after text filtering','gold'),
            stat('Discovered topics',str(B['topics']),'NMF model selected for Task B'),
        ],className='grid grid-4'),
        html.Div([
            panel('Campaign outcome',graph(fig_subscription()),'Subscribed vs. not subscribed · Task A'),
            panel('Cluster performance',graph(fig_cluster_rates()),'Observed subscription rate by K-Means cluster; this is post-hoc, not a prediction.'),
        ],className='grid grid-2 section'),
        html.Div([
            panel('Most prevalent NMF topics',graph(fig_topic_prevalence(),height=470),
                  'Number of documents assigned to their highest-weighted topic.'),
            panel('Analysis at a glance',[
                html.Div('01 · Structured data',className='method-title'),
                html.P(f"Eight numerical features standardised → PCA → {A['retained_pcs']} components → "
                       f"{A['best_k']} K-Means clusters. Retained variance: {pct(A['retained_variance'],2)}.",className='method-copy'),
                html.Hr(),
                html.Div('02 · Text analytics',className='method-title'),
                html.P(f"20 Newsgroups corpus cleaned → {comma(B['usable_docs'])} usable posts → "
                       f"{comma(B['vocab'])} TF-IDF features → {B['topics']} NMF topics.",className='method-copy'),
                html.Hr(),
                html.Div('03 · Interactive exploration',className='method-title'),
                html.P('Open the pages on the left to change chart metrics, inspect cluster characteristics, browse topic keywords, and download the topic summary.',className='method-copy'),
                callout('These datasets describe different domains. Their outcomes must not be treated as causally linked.', 'Interpretation note:')
            ]),
        ],className='grid grid-2 section'),
        html.P('Source: outputs stored in Task_A_Bank_Marketing(10).ipynb and Task_B_20Newsgroups_NMF_Complete(5).ipynb.',className='footer-note')
    ])


def bank_page():
    return page([
        heading('Task A · exploration','Bank marketing performance','Review the original dataset, response patterns, and contact-history signals. Use the selectors to explore different views.'),
        html.Div([
            stat('Total observations',comma(A['records']),'No rows dropped during Task A cleaning','blue'),
            stat('Successful subscriptions',comma(A['subscribed']),pct(A['subscribed']/A['records'],2)+' of observations'),
            stat('Previous campaign contacts',comma(A['previous_gt_zero']),'Observations with previous > 0','gold'),
            stat('Known days since prior contact',comma(A['non_null_pdays']),'Observations with pdays ≠ 999'),
        ], className='grid grid-4'),
        callout('`previous > 0` counts contacts before the present campaign; `pdays ≠ 999` identifies a known interval since the last prior contact. These are not the same measure.', 'Contact-history distinction:'),
        html.Div([
            panel('Campaign activity by month',[
                select('month-metric',[{'label':'Subscription rate (%)','value':'subscription_rate'}, {'label':'Number of observations','value':'records'}], 'subscription_rate','Display metric'),
                graph(id='month-chart',height=330),
            ], 'Month categories in chronological calendar order (not a chronological time series across years).'),
            panel('Customer occupations',[
                select('job-limit',[{'label':'Top 6 occupations','value':6},{'label':'Top 10 occupations','value':10},{'label':'All occupations','value':12}],10,'Categories displayed'),
                graph(id='job-chart',height=340),
            ], 'Number of observations per occupation.'),
        ],className='grid grid-2 section'),
        html.Div([
            panel('Prior-contact associations',[
                graph(fig_prior_contacts(),height=315),
            ], 'Subscription rates are associations, not evidence that contact history causes subscription.'),
            panel('Supporting figures from Task A',[
                image('a_01_age.png','Age distribution from the source notebook.'),
                html.Br(),
                image('a_09_correlation.png','Correlation heatmap, displayed as a saved snapshot.'),
            ]),
        ],className='grid grid-2 section'),
    ])


def fig_prior_contacts():
    df=CONTACT.sort_values('previously_contacted')
    fig=base_figure(315)
    fig.add_bar(x=['Previous = 0','Previous > 0'],y=df['subscription_rate'],marker_color=[BLUE,TEAL],
                text=[f'{v:.1f}%' for v in df.subscription_rate],textposition='outside',
                customdata=df['count'],
                hovertemplate='%{x}<br>Subscription rate: %{y:.2f}%<br>Observations: %{customdata:,}<extra></extra>')
    fig.update_yaxes(title='Subscription rate (%)',range=[0,32])
    return fig


def pca_page():
    return page([
        heading('Task A2 · dimensionality reduction','What drives the principal components?',
                'Eight standardised numerical variables were reduced using PCA. Explore explained variance and the signed feature loadings.'),
        html.Div([
            stat('Input features',str(A['features']),'Original numeric features used','blue'),
            stat('Retained components',str(A['retained_pcs']),'Minimum number reaching 90% variance'),
            stat('Variance retained',pct(A['retained_variance'],2),'Cumulative explained variance','gold'),
            stat('Unretained variance',pct(1-A['retained_variance'],2),'Information not represented by retained PCs'),
        ],className='grid grid-4'),
        html.Div([
            panel('Explained variance',graph(fig_pca_variance(),height=340),
                  'Bars show individual variance ratios; the line shows cumulative retention.'),
            panel('Principal component loadings',[
                select('pc-select',[{'label':pc,'value':pc} for pc in [c for c in PCA_LOADINGS.columns if c.startswith('PC')]],'PC1',
                       'Choose principal component'),
                graph(id='loading-chart',height=350),
            ], 'Positive and negative loadings indicate direction; interpretation also depends on their magnitude.'),
        ],className='grid grid-2 section'),
        html.Div([
            panel('PCA projection (saved original plot)',image('a_13_pca_scatter.png',
                  'Exact plotted sample/coordinates from the original notebook. Per-point filtering requires the row-level export CSV.')),
            panel('Complete component loading heatmap',image('a_12_pca_loadings.png',
                  'PCA loading heatmap from the notebook, included for full component interpretation.')),
        ],className='grid grid-2 section'),
        callout('PCA preserves variance, not necessarily business relevance. The economic indicators may reflect campaign periods rather than stable characteristics of individual customers.', 'Limitation:')
    ])


def clustering_page():
    cl0=CLUSTER_PROFILES.loc[CLUSTER_PROFILES.cluster==0].iloc[0]
    cl1=CLUSTER_PROFILES.loc[CLUSTER_PROFILES.cluster==1].iloc[0]
    metrics=['age','campaign','previous','emp.var.rate','cons.price.idx','cons.conf.idx','euribor3m','nr.employed','subscribed','previously_contacted']
    return page([
        heading('Task A3 · K-Means','Explore discovered customer segments',
                'K-Means fitted on the existing PCA representation. View cluster sizes, campaign outcomes, numerical profiles and categorical composition.'),
        html.Div([
            stat('Selected K',str(A['best_k']),'Highest sampled silhouette across K=2–8','blue'),
            stat('Silhouette score',f"{A['silhouette']:.3f}",'Fixed evaluation subsample'),
            stat('Cluster 0',comma(int(cl0['size'])),pct(float(cl0['share']))+' of observations','gold'),
            stat('Cluster 1',comma(int(cl1['size'])),pct(float(cl1['share']))+' of observations'),
        ],className='grid grid-4'),
        html.Div([
            panel('Compare numerical cluster profiles',[
                select('cluster-metric',[{'label':x.replace('.',' · ').replace('_',' ').title(),'value':x} for x in metrics],
                       'euribor3m','Feature / outcome'),
                graph(id='cluster-metric-chart',height=345),
            ], 'Binary outcomes are shown as percentages; other variables use original measurement units.'),
            panel('Compare categorical composition',[
                select('composition-field',[{'label':x.title(),'value':x} for x in COMPOSITIONS], 'job', 'Categorical variable'),
                graph(id='composition-chart',height=370),
            ], 'Within each cluster, proportions sum to approximately 100% (rounding may apply).'),
        ],className='grid grid-2 section'),
        html.Div([
            panel('Cluster subscription rates',graph(fig_cluster_rates(),height=320),
                  'Post-hoc outcome comparison; subscription was not used to fit K-Means.'),
            panel('Cluster profiles — recorded findings',[
                html.Div('Cluster 0 · higher rate / lower response',className='method-title'),
                html.P(f"{comma(cl0['size'])} observations; mean Euribor 3m {cl0['euribor3m']:.2f}; "
                       f"subscription {pct(cl0['subscribed'])}; mean previous contacts {cl0['previous']:.3f}.",className='method-copy'),
                html.Hr(),
                html.Div('Cluster 1 · lower rate / higher response',className='method-title'),
                html.P(f"{comma(cl1['size'])} observations; mean Euribor 3m {cl1['euribor3m']:.2f}; "
                       f"subscription {pct(cl1['subscribed'])}; mean previous contacts {cl1['previous']:.3f}.",className='method-copy'),
                html.Hr(),
                html.Div('Marketing interpretation',className='method-title'),
                html.P('The clusters differ strongly in macroeconomic context as well as observed outcomes. They should not be interpreted as two fixed customer personality types.',className='method-copy'),
            ]),
        ],className='grid grid-2 section'),
        html.Div([
            panel('Choosing the number of clusters',[
                graph(fig_k_selection(),height=290),
                image('a_14_elbow_silhouette.png','Saved two-panel elbow and sampled-silhouette figure.'),
            ], 'The candidate search evaluated K=2 through K=8.'),
            panel('Visual cluster representation',[
                image('a_16_cluster_scatter_rates.png','PCA cluster projection from the notebook. This is an exact saved visual, not synthetic points.'),
                html.Br(),
                image('a_15_cluster_heatmap.png','Standardized differences from overall feature means.'),
            ]),
        ],className='grid grid-2 section'),
    ])


def fig_k_selection():
    fig=base_figure(290)
    x=CLUSTER_METRICS.k
    fig.add_scatter(x=x,y=CLUSTER_METRICS.silhouette_sample,mode='lines+markers',
                    line=dict(color=TEAL,width=3),name='Sample silhouette',
                    hovertemplate='K=%{x}: %{y:.3f}<extra></extra>')
    fig.add_vline(x=A['best_k'],line_dash='dash',line_color=BLUE)
    fig.update_xaxes(title='K',dtick=1)
    fig.update_yaxes(title='Sample silhouette')
    return fig


def text_page():
    return page([
        heading('Task B1 & B2 · topic modeling','From raw posts to interpretable themes',
                'Inspect the text-quality audit, choose an evaluation metric, and review how the NMF topic count was selected.'),
        html.Div([
            stat('Original texts',comma(B['original_docs']),'20 Newsgroups corpus','blue'),
            stat('Usable documents',comma(B['usable_docs']),'After quality filters and zero-term removal'),
            stat('TF-IDF features',comma(B['vocab']),'Unigrams and bigrams','gold'),
            stat('Selected topics',str(B['topics']),'Latent NMF factors'),
        ],className='grid grid-4'),
        html.Div([
            panel('NMF topic-count evaluation',[
                select('nmf-metric',[
                    {'label':'Topic separation (higher is better)','value':'topic_separation'},
                    {'label':'Top-term uniqueness (higher is better)','value':'top_term_uniqueness'},
                    {'label':'Reconstruction error (lower is better)','value':'reconstruction_error'},
                ],'topic_separation','Evaluation metric'),
                graph(id='nmf-selection-chart',height=355),
            ], 'The 12-topic choice balances distinguishable themes, keyword uniqueness and interpretability.'),
            panel('Cleaning and vectorisation audit',[
                html.Table([
                    html.Thead(html.Tr([html.Th('Stage'),html.Th('Remaining'),html.Th('Removed')])),
                    html.Tbody([
                        html.Tr([html.Td(str(row['Stage'])),html.Td(comma(row['Records remaining'])),
                                 html.Td(comma(row['Records removed at stage']))])
                        for _,row in TEXT_AUDIT.iterrows()
                    ])
                ],className='mini-table'),
                html.P('TF-IDF stop-word filtering and vocabulary restrictions occur after document cleaning. Only non-empty TF-IDF rows are passed to NMF.',className='small-stat'),
                html.P('A repeated newsgroup signature was removed from the raw text before refitting NMF.',className='small-stat'),
            ]),
        ],className='grid grid-2 section'),
        html.Div([
            panel('Text length and category distribution',image('b_01_text_lengths.png','Two exploratory charts from Task B1.')),
            panel('Term frequencies',image('b_02_terms.png','Most widespread terms and mean TF-IDF term weights from Task B1.')),
        ],className='grid grid-2 section'),
        callout('The 20 original newsgroup categories are not NMF target labels. The topic model is unsupervised; the selected K need not equal the original 20 categories.', 'Method note:')
    ])


def topic_page():
    return page([
        heading('Task B2 · topic explorer','Discover and compare the 12 NMF topics',
                'Use the topic selector to inspect significant keywords and representative text excerpts. Compare prevalence by document assignments or normalized topic weights.'),
        html.Div([
            panel('Topic prevalence',[
                select('topic-metric',[
                    {'label':'Dominant document share (%)','value':'dominant_share'},
                    {'label':'Number of dominant documents','value':'dominant_documents'},
                    {'label':'Mean relative topic weight (%)','value':'mean_relative_weight'},
                ],'dominant_share','Compare topics using'),
                graph(id='topic-prevalence-chart',height=470),
            ], 'Dominant assignments and normalized weights are different measures.'),
            panel('Selected topic',[
                select('topic-select',[
                    {'label':f"Topic {int(row.topic_id)+1:02d} — {row.label}", 'value':int(row.topic_id)}
                    for row in TOPIC_SUMMARY.itertuples()
                ],0,'Select a discovered topic'),
                html.Div(id='topic-detail'),
            ], 'Keywords and example passages are from the final saved model.'),
        ],className='grid grid-2 section'),
        html.Div([
            panel('All topics: important term weights',image('b_04_topic_terms.png',
                  'Actual NMF term-weight plots from the source notebook.')),
            panel('Original categories versus discovered topics',image('b_06_category_topic.png',
                  'Diagnostic comparison only; original category labels were not used in training.')),
        ],className='grid grid-2 section'),
        html.Div([
            html.Button('Download topic summary (.csv)',id='download-topic-btn',className='btn'),
            dcc.Download(id='download-topic-summary'),
            html.Span(' Includes labels, top terms, prevalence and mean relative weights.',className='small-stat'),
        ],className='row-flex section'),
        callout('Some topics (e.g., requests for information or general opinions) are communication styles rather than strict subjects. Interpret topic labels as descriptive summaries, not verified ground truth.', 'Caution:')
    ])



PAGE_ITEMS = [
    ('/','Overview','▦'),
    ('/bank','Bank Marketing EDA','◫'),
    ('/pca','PCA Analysis','◇'),
    ('/clusters','Customer Clusters','◎'),
    ('/text','Text Preparation & NMF','☰'),
    ('/topics','Topic Explorer','✦'),
]
PAGE_BUILDERS = {
    '/': overview_page,
    '/bank': bank_page,
    '/pca': pca_page,
    '/clusters': clustering_page,
    '/text': text_page,
    '/topics': topic_page
}

app.layout = html.Div([
    dcc.Location(id='route',refresh=False),
    html.Aside([
        html.Div([
            html.Div('A',className='brand-mark'),
            html.Span('AIT2309961',className='brand-title'),
            html.Div('Task C: Analytical Application',className='brand-sub'),
        ],className='brand'),
        html.Div('Explore reports',className='nav-label'),
        html.Div(id='nav-menu',className='nav-wrap'),
    ],className='sidebar'),
    html.Main([
        html.Header([
            html.Div('ADVANCED DATA ANALYTICS  /  TASK C',className='topbar-left'),
            html.Div('Notebook-derived · No model retraining',className='topbar-badge'),
        ],className='topbar'),
        html.Div(id='page-content'),
    ],className='main'),
],className='app-shell')


@app.callback(Output('nav-menu','children'),Output('page-content','children'),Input('route','pathname'))
def render_route(pathname):
    route=pathname if pathname in PAGE_BUILDERS else '/'
    links=[dcc.Link([
        html.Span(symbol,className='nav-icon'),html.Span(title)
    ], href=path, className='nav-item'+(' nav-active' if route==path else ''))
           for path,title,symbol in PAGE_ITEMS]
    return links,PAGE_BUILDERS[route]()


@app.callback(Output('month-chart','figure'),Input('month-metric','value'))
def update_month(value):
    return fig_month(value or 'subscription_rate')

@app.callback(Output('job-chart','figure'),Input('job-limit','value'))
def update_jobs(value):
    return fig_jobs(value or 10)

@app.callback(Output('loading-chart','figure'),Input('pc-select','value'))
def update_pc(value):
    return fig_pc_loading(value or 'PC1')

@app.callback(Output('cluster-metric-chart','figure'),Input('cluster-metric','value'))
def update_cluster_metric(value):
    return fig_cluster_metric(value or 'euribor3m')

@app.callback(Output('composition-chart','figure'),Input('composition-field','value'))
def update_composition(value):
    return fig_composition(value or 'job')

@app.callback(Output('nmf-selection-chart','figure'),Input('nmf-metric','value'))
def update_nmf_evaluation(value):
    return fig_topic_selection(value or 'topic_separation')

@app.callback(Output('topic-prevalence-chart','figure'),Input('topic-metric','value'))
def update_topic_prevalence(value):
    return fig_topic_prevalence(value or 'dominant_share')

@app.callback(Output('topic-detail','children'),Input('topic-select','value'))
def update_topic_detail(topic_id):
    topic_id=int(topic_id or 0)
    matches=TOPIC_SUMMARY.loc[TOPIC_SUMMARY.topic_id==topic_id]
    if matches.empty:
        return html.P('Topic not found.')
    r=matches.iloc[0]
    chips=[html.Span(t.strip(),className='pill'+(' pill-index' if i<3 else ''))
           for i,t in enumerate(str(r.top_terms).split(','))]
    excerpts=REPRESENTATIVES.loc[REPRESENTATIVES.topic_id==topic_id].sort_values('rank')
    rep_cards=[html.Div([
        html.Div(f'EXCERPT {int(rec["rank"])} · Relative topic weight {float(rec["relative_weight"]):.2f}',className='excerpt-label'),
        html.Div(str(rec['excerpt'])+'…')
    ],className='excerpt') for _,rec in excerpts.iterrows()]
    if not rep_cards: rep_cards=[html.Div('Representative documents were not available in the saved notebook output.')]
    return html.Div([
        html.Div(f'TOPIC {topic_id+1:02d}',className='topic-num'),
        html.Div(str(r.label),className='topic-name'),
        html.Div(f"{comma(r.dominant_documents)} dominant documents · {pct(r.dominant_share,2)} of usable posts · "
                 f"{pct(r.mean_relative_weight,2)} mean normalized weight",className='topic-meta'),
        html.Div('IMPORTANT TERMS',className='filter-label'),
        html.Div(chips),
        html.Div('REPRESENTATIVE POSTS (EXCERPTS)',className='filter-label',style={'marginTop':'20px'}),
        *rep_cards,
    ])


@app.callback(Output('download-topic-summary','data'),Input('download-topic-btn','n_clicks'),prevent_initial_call=True)
def download_topic_summary(n):
    return dcc.send_data_frame(TOPIC_SUMMARY.to_csv,'task_b_nmf_topic_summary.csv',index=False)


if __name__=='__main__':
    import os
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT','8050')),debug=False)

#!/usr/bin/env python
# coding: utf-8

# ## Quantitative comparisons
# 
# Can we express quantitatively what we observed in the previous plots? This is where the meta-analysis tools come in: we used the R package [metafor](http://www.metafor-project.org/doku.php) to fit a mixed-effect (ME) model to the data reported for each measure. In this way, we can estimate an overall interval of R<sup>2</sup> values based on the effect sizes and the sample sizes. We can also estimate the interval of R<sup>2</sup> that we can expect in future studies (this is called prediction interval). 
# 
# ```{admonition} Figure 5
# :class: tip
# A compact way to represent these results is given by forest plots: for each study, we represent the effect size and the related sample size using a square and a horizontal error bar; then for each measure, we represent the results from the ME model using a diamond and an additional error bar; finally to represent the prediction interval we use two hourglasses and a dotted line.
# ```

# In[1]:


import numpy as np
import pandas as pd

import plotly.graph_objects as go
from IPython.core.display import display, HTML
from plotly.offline import plot
import plotly.express as px
import plotly.colors
from plotly.subplots import make_subplots

from rpy2.robjects.packages import importr
import rpy2.robjects
import subprocess
subprocess.call('curl https://raw.githubusercontent.com/Notebook-Factory/brand/main/insertLogo.py --output /tmp/insertLogo.py', shell=True)
get_ipython().run_line_magic('run', '/tmp/insertLogo.py')


# ### Figure 5

# In[15]:


config={'showLink': False, 'displayModeBar': False}

filtered_df = pd.read_pickle("filtered_df.pkl")

filtered_df['Variance'] = (4*filtered_df['R^2'])*((1-filtered_df['R^2'])**2)/filtered_df['Sample points']

measure_type = {'Diffusion':['RD', 'AD', 'FA', 'MD',
                'AWF', 'RK', 'RDe', 'MK'],
                'Magnetization transfer':['MTR',
                'ihMTR', 'MTR-UTE', 'MPF', 'MVF-MT',
                'R1f', 'T2m', 'T2f', 'k_mf','k_fm'],
                'T1 relaxometry':['T1'], 'T2 relaxometry':['T2', 'MWF', 'MVF-T2'],
                'Other':['QSM', 'R2*', 'rSPF', 'MTV',
                'T1p', 'T2p', 'RAFF', 'PD', 'T1sat']}

color_dict = {m:plotly.colors.qualitative.Bold[n]
              for n,m in enumerate(measure_type.keys())}

metafor = importr('metafor')
stats = importr('stats')

metastudy = {}
for m in filtered_df.Measure.unique():
    nstudies=len(filtered_df.Measure[filtered_df.Measure==m])
    if nstudies > 2:
        df_m = filtered_df[filtered_df.Measure==m]
        df_m = df_m.sort_values(by=['Year'])
        
        r2 = rpy2.robjects.FloatVector(df_m['R^2'])
        var = rpy2.robjects.FloatVector(df_m['Variance'])
        fit = metafor.rma(r2, var, method="REML", test="knha")
        res = stats.predict(fit)
        
        results = dict(zip(res.names,list(res)))
        
        metastudy[m] = dict(pred=results['pred'][0], cilb=results['pred'][0]-results['ci.lb'][0],
                            ciub=results['ci.ub'][0]-results['pred'][0],
                            crub=results['cr.ub'][0], 
                            crlb=results['cr.lb'][0])
measure_type_reverse={m:t for t,mlist in measure_type.items() for m in mlist}
fig5 = make_subplots(rows=3, cols=3, start_cell="top-left", vertical_spacing=0.06,
                      horizontal_spacing=0.2, x_title='R<sup>2</sup>',
                      subplot_titles=sorted(metastudy.keys(), key=measure_type_reverse.get))

row=1
col=1
for m in sorted(metastudy.keys(), key=measure_type_reverse.get):
    fig5.add_trace(go.Scatter(
        x=[round(metastudy[m]['crlb'],2) if round(metastudy[m]['crlb'],2)>0 else 0,
           round(metastudy[m]['crub'],2) if round(metastudy[m]['crub'],2)<1 else 1],
        y=['Mixed model','Mixed model'],
        line=dict(color='black', width=2, dash='dot'),
        hovertemplate = 'Prediction boundary: %{x}<extra></extra>',
        marker_symbol = 'hourglass-open', marker_size = 8
    ), row=row, col=col)
    
    fig5.add_trace(go.Scatter(
        x=[round(metastudy[m]['pred'],2)],
        y=['Mixed model'],
        mode='markers',
        marker = dict(color = 'black'),
        marker_symbol = 'diamond-wide',
        marker_size = 10,
        hovertemplate = 'R<sup>2</sup> estimate: %{x}<extra></extra>',
        error_x=dict(
            type='data',
            arrayminus=[round(metastudy[m]['cilb'],2) if round(metastudy[m]['cilb'],2)>0 else 0],
            array=[round(metastudy[m]['ciub'],2) if round(metastudy[m]['ciub'],2)<1 else 1])
    ), row=row, col=col)
    
    df_m = filtered_df[filtered_df.Measure==m]
    df_m = df_m.sort_values(by=['Year'], ascending=False)
    fig5.add_trace(go.Scatter(
        x=df_m['R^2'],
        y=df_m['Study'],
        text=df_m['Sample points'],
        customdata=df_m['Histology/microscopy measure'],
        mode='markers',
        marker = dict(color = color_dict[measure_type_reverse[m]]),
        marker_symbol = 'square',
        marker_size = np.log(50/df_m['Variance']),
        hovertemplate = '%{y}<br>R<sup>2</sup>: %{x}<br>Number of samples: %{text}' +
            '<br>Reference: %{customdata}<extra></extra>',
        error_x=dict(
            type='data',
            array=2*np.sqrt(df_m['Variance']))
    ), row=row, col=col)

    if col == 3:
        col = 1
        row += 1
    else:
        col += 1

fig5.update_xaxes(range=[0, 1])

fig5.update_yaxes(tickfont=dict(size=8))

fig5.update_layout(showlegend=False,
    title=dict(text='Figure 5: Forest plots and mixed modelling results'),
    margin=dict(l=0),
    width=700,
    height=800)

for ii in range(9):
    fig5.layout.annotations[ii]["font"] = {'size': 10,'color':'black'}

plot(insertLogo(fig5,0.03,0.03,1,-0.07,-0.125,0.033), filename = 'fig5.html',config = config)
display(HTML('fig5.html'))


# The forest plot offers a detailed summary for each measure. What if we want to compare the R<sup>2</sup> estimates across measures? To do that, we pooled together all the measures from all the studies and computed first a repeated measures meta-regression and then all the possible pairwise comparisons (Tukey's test), correcting for multiple comparisons (Bonferroni correction). 
# 
# ```{admonition} Figure 6
# :class: tip
# To visually represent these results, we used two heatmaps, one for the z-scores and one for the p-values: each element refers to the comparison between the measure on the x axis and the one on the y axis.
# ```

# ### Figure 6

# In[26]:


multcomp = importr('multcomp')
base = importr('base')

thres = filtered_df.Measure.value_counts() > 2
df_thres = filtered_df[filtered_df.Measure.isin(filtered_df.Measure.value_counts()[thres].index)]
r2 = rpy2.robjects.FloatVector(df_thres['R^2'])
var = rpy2.robjects.FloatVector(df_thres['Variance'])
measure_v = rpy2.robjects.StrVector(df_thres['Measure'])
measure_f = rpy2.robjects.Formula('~ -1 + measure')
env = measure_f.environment
env['measure'] = measure_v
study_v = rpy2.robjects.StrVector(df_thres['Study'])
study_f = rpy2.robjects.Formula('~ 1 | study')
env = study_f.environment
env['study'] = study_v
fit_mv = metafor.rma_mv(r2, var, method="REML", mods=measure_f, random=study_f)

glht = multcomp.glht(fit_mv, base.cbind(multcomp.contrMat(base.rep(1,9), type="Tukey")))
mtests = multcomp.summary_glht(glht, test=multcomp.adjusted("bonferroni"))
mtest_res = dict(zip(mtests.names, list(mtests)))
stat_res = dict(zip(mtest_res['test'].names, list(mtest_res['test'])))
pvals = stat_res['pvalues']
zvals = stat_res['tstat']

measure_list = df_thres['Measure'].unique()
measure_list.sort()
n = len(measure_list)

pvals_list = []
zvals_list = []
idx = 0
for i in range(n):
    pvals_i = [0] * i
    pvals_i.append(np.nan)
    pvals_i.extend(pvals[idx:idx+n-i-1])
    zvals_i = [0] * i
    zvals_i.append(np.nan)
    zvals_i.extend(zvals[idx:idx+n-i-1])
    idx = idx + n - i - 1
    pvals_list.append(pvals_i)
    zvals_list.append(zvals_i)

pvals_list=np.array(pvals_list)    
zvals_list=np.array(zvals_list)
pvals_list=pvals_list+pvals_list.T
zvals_list=zvals_list-zvals_list.T
    
fig6 = make_subplots(rows=1, cols=2, horizontal_spacing=0.14,
                     subplot_titles=['z-scores',
                                     'p-values'
                                    ])

fig6.add_trace(go.Heatmap(
    z=zvals_list,
    x=measure_list,
    y=measure_list,
    customdata=pvals_list,
    hovertemplate = '%{x}-%{y}<br>z-score: %{z:.2f}<br>p-value: %{customdata:.5f}<extra></extra>',
    hoverongaps = False,
    colorscale='RdBu',
    colorbar=dict(title='z-score', x=0.42,thickness=20),
    showscale=True
), col=1, row=1)

fig6.add_trace(go.Heatmap(
    z=pvals_list,
    x=measure_list,
    y=measure_list,
    customdata=zvals_list,
    hovertemplate = '%{x}-%{y}<br>z-score: %{customdata:.2f}<br>p-value: %{z:.5f}<extra></extra>',
    hoverongaps = False,
    colorscale='Purples',
    colorbar=dict(title='p-value',thickness=20),
    zmin=0,
    zmax=0.05,
    showscale=True,
    reversescale=True
), col=2, row=1)

fig6.update_layout(
    title='Figure 6: Statistical pairwise comparisons between R<sup>2</sup> estimates',
    width=740,
    height = 420,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0,r=0)
)

plot(insertLogo(fig6,0.07,0.07,1.11,-0.15,-0.1,0.075), filename = 'fig6.html',config = config)
display(HTML('fig6.html'))


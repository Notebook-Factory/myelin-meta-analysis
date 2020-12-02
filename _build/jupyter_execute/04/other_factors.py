#!/usr/bin/env python
# coding: utf-8

# ## Potential confounders
# Can some of this variance be explained by the differences in methodological choices and experimental conditions we mention? The number of studies is limited for a quantitative evaluation, but we can get a qualitative idea using bar plots and scatter plots organized by each condition.
# 
# ```{admonition} Figure 7
# :class: tip
# Distributions of R<sup>2</sup> values in relation to the reference techniques, pathology and tissue types are visualized using box plots. You can mouse over markers to see the studies they are drawn from.
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


# ### Figure 7

# In[11]:


config={'showLink': False, 'displayModeBar': False}

metafor = importr('metafor')
stats = importr('stats')

filtered_df = pd.read_pickle("filtered_df.pkl")

filtered_df['Variance'] = (4*filtered_df['R^2'])*((1-filtered_df['R^2'])**2)/filtered_df['Sample points']

structures={'Lesions':'Lesions',
            'Substantia nigra':'Deep grey matter',
            'Hippocampal commissure':'White matter',
            'Putamen':'Deep grey matter',
            'Motor cortex':'Grey matter',
            'Globus pallidus':'Deep grey matter',
            'Perforant pathway':'White matter',
            'Mammilothalamic tract':'White matter',
            'External capsule':'White matter',
            'Inter-peduncular nuclues':'Deep grey matter',
            'Hippocampus':'Deep grey matter',
            'Thalamic nuclei':'Deep grey matter',
            'Thalamus':'Deep grey matter',
            'Cerebellum':'Grey matter',
            'Amygdala':'Deep grey matter',
            'Cingulum':'White matter',
            'Striatum':'Deep grey matter',
            'Accumbens':'Deep grey matter',
            'Basal ganglia':'Deep grey matter',
            'Anterior commissure':'White matter',
            'Cortex':'Grey matter',
            'Fimbria':'White matter',
            'Somatosensory cortex':'Grey matter',
            'Dorsal tegmental tract':'White matter',
            'Superior colliculus':'Deep grey matter',
            'Fasciculus retroflexus':'White matter',
            'Optic nerve':'White matter',
            'Dentate gyrus':'Grey matter',
            'Corpus callosum':'White matter',
            'Fornix':'White matter',
            'White matter':'White matter',
            'Grey matter':'Grey matter',
            'Optic tract':'White matter',
            'Internal capsule':'White matter',
            'Stria medullaris':'White matter'}


tissue_types=[]
for s in filtered_df['Specific structure(s)']:
    t_list=[]
    for i in s.split(','):
        t_list.append(structures[i.strip()])
    tissue_types.append('+'.join(list(set(t_list))))

filtered_df['Tissue types']=tissue_types

fig7 = make_subplots(rows=3, cols=1, start_cell="top-left", vertical_spacing=0.2, y_title='R<sup>2</sup>',
                     subplot_titles=['R<sup>2</sup> values and reference techniques',
                                     'R<sup>2</sup> values and pathology',
                                     'R<sup>2</sup> values and tissue types'])

references = ['Histology', 'Immunohistochemistry', 'Microscopy', 'EM']

for r in references:
    df_r=filtered_df[filtered_df['Histology/microscopy measure'].str.contains(r)]
    fig7.add_trace(go.Box(
        y=df_r['R^2'],
        x=df_r['Histology/microscopy measure'],
        boxpoints='all',
        text=df_r['Measure'] + ' - ' + df_r['Study'],
        name=r
    ), col=1, row=1)

for t in filtered_df['Condition'].unique():
    df_t=filtered_df[filtered_df['Condition']==t]
    fig7.add_trace(go.Box(
        y=df_t['R^2'],
        x=df_t['Condition'],
        boxpoints='all',
        text=df_t['Measure'] + ' - ' + df_t['Study'],
        name=t
    ), col=1, row=2)

for t in filtered_df['Tissue types'].unique():
    df_t=filtered_df[filtered_df['Tissue types']==t]
    fig7.add_trace(go.Box(
        y=df_t['R^2'],
        x=df_t['Tissue types'],
        boxpoints='all',
        text=df_t['Measure'] + ' - ' + df_t['Study'],
        name=t
    ), col=1, row=3)   

fig7.update_layout(
    title=dict(
        text='Figure 7: Experimental conditions and methodological choices influencing the R<sup>2</sup> values',
        x=0),
    margin=dict(l=0),
    showlegend=False,
    height=1000,
    width=600
)

fig7.update_xaxes(tickfont=dict(size=10))
plot(insertLogo(fig7,0.03,0.03,1,-0.149,-0.125,0.025), filename = 'fig7.html',config = config)
display(HTML('fig7.html'))


# 
# ```{admonition} Figure 8
# :class: tip
# Other potential confounders include magnetic field strength, tissue conditions, co-registration and tissue type. You can mouse over markers in each panel to see the corresponding studies.
# ```
# 
# ### Figure 8

# In[23]:


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

fig8 = make_subplots(rows=2, cols=2, start_cell="top-left", vertical_spacing=0.18, y_title='R<sup>2</sup>',
                     subplot_titles=['R<sup>2</sup> values and magnetic fields',
                                     'R<sup>2</sup> values and tissue conditions',
                                     'R<sup>2</sup> values and co-registration',
                                     'R<sup>2</sup> values and human/animal tissue'
                                    ])

for m in measure_type.keys():
    df_m=filtered_df[filtered_df["Measure"].isin(measure_type[m])]
    fig8.add_trace(go.Scatter(x=df_m['Magnetic field'],
                              y=df_m['R^2'],
                              text=df_m['Measure'] + ' - ' + df_m['Study'],
                              marker=dict(color=color_dict[m]),
                              name=m,
                              mode='markers'), col=1, row=1)

fig8.update_layout(
    xaxis=dict(title='Magnetic field [T]')
)

for t in filtered_df['Tissue condition'].unique():
    df_t=filtered_df[filtered_df['Tissue condition']==t]
    fig8.add_trace(go.Box(
        y=df_t['R^2'],
        x=df_t['Tissue condition'],
        boxpoints='all',
        text=df_t['Measure'] + ' - ' + df_t['Study'],
        name=t
    ), col=2, row=1)
    
for t in filtered_df['Co-registration'].unique():
    df_t=filtered_df[filtered_df['Co-registration']==t]
    fig8.add_trace(go.Box(
        y=df_t['R^2'],
        x=df_t['Co-registration'],
        boxpoints='all',
        text=df_t['Measure'] + ' - ' + df_t['Study'],
        name=t
    ), col=1, row=2)
    
for t in filtered_df['Human/animal'].unique():
    df_t=filtered_df[filtered_df['Human/animal']==t]
    fig8.add_trace(go.Box(
        y=df_t['R^2'],
        x=df_t['Human/animal'],
        boxpoints='all',
        text=df_t['Measure'] + ' - ' + df_t['Study'],
        name=t
    ), col=2, row=2)

fig8.update_layout(
    title=dict(text='Figure 8: Other factors to consider when assessing R<sup>2</sup>', x=0.1),
    margin=dict(l=100),
    showlegend=False,
    height=600,
    width=700
)    
  
plot(insertLogo(fig8,0.04,0.04,1,-0.2,-0.12,0.048), filename = 'fig8.html',config = config)
display(HTML('fig8.html'))


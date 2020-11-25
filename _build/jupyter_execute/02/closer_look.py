#!/usr/bin/env python
# coding: utf-8

# ## Sample size and effect size
# 
# Given the number of different variables influencing the results, we decided to focus only on brain studies. As we needed to take into account the sample size for quantitative comparisons, we also further selected only the studies that reported both the number of subjects and the number of ROIs (regions of interest) considered for correlation purposes. This further screening led us to 43 studies. For these studies we wanted to quantitatively evaluate the reported effect size taking into account the respective samples sizes: we chose the coefficient of determination R<sup>2</sup>, as it was the most common quantitative result we could obtain from these studies.
# 
# ```{admonition} Figure 3
# :class: tip
# To have a look at both sample size and effect size for each measure, we prepared an interactive bubble chart, where the size of each bubble is proportional to the sample size. You can hover on the bubbles to obtain additional details.
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


# ### Figure 3

# In[3]:


config={'showLink': False, 'displayModeBar': False}

info = pd.read_excel('database.xlsx', sheet_name='Details')

year_str = info['Year'].astype(str)
info['Study'] = info['First author'] + ' et al., ' + year_str
info['Study'] = info.groupby('Study')['Study'].apply(lambda n: n+list(map(chr,np.arange(len(n))+97))
                                                     if len(n)>1 else n)
info['Number of studies'] = np.ones((len(info),1))
info = info.sort_values('Study')

info['Link'] = info['DOI']
info['Link'].replace('http',"""<a style='color:white' href='http""",
                    inplace=True, regex=True)
info['Link'] = info['Link'] + """'>->Go to the paper</a>"""

fields = ['Approach', 'Magnetic field', 'MRI measure(s)',
          'Histology/microscopy measure', 'Specific structure(s)']
info['Summary'] = info['Link'] + '<br><br>'
for i in fields:
    info['Summary'] = info['Summary'] + i + ': ' + info[i].astype(str) + '<br><br>'

df = pd.DataFrame()
data = pd.read_excel('database.xlsx', sheet_name='R^2')

measures = data.columns[1:]
for _, row in data.iterrows():
    measure_avail = {m:value for m, value in zip(measures, row.tolist()[1:])
                    if not np.isnan(value)}
    for m in measure_avail.keys():
        df = df.append([[row.DOI, m, measure_avail[m],
                         *info[info.DOI==row.DOI].values.tolist()[0][1:]]])
df.columns = ['DOI', 'Measure', 'R^2', *info.columns[1:]]

df['ROI per subject'] = pd.to_numeric(df['ROI per subject'], errors='coerce')
df['Subjects'] = pd.to_numeric(df['Subjects'], errors='coerce')
df = df.dropna(subset=['ROI per subject', 'Subjects'])
df = df[df['ROI per subject']<100]
df['Sample points'] = df['ROI per subject'] * df['Subjects']

df=df.sort_values(by=['Measure'])

filtered_df=df[df.Focus=='Brain'].copy()

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

hover_text = []
bubble_size = []

for index, row in filtered_df.iterrows():
    hover_text.append(('Measure: {measure}<br>'+
                      'Number of subjects: {subjects}<br>'+
                      'ROIs per subject: {rois}<br>'+
                      'Total number of samples: {samples}').format(measure=row['Measure'],
                                            subjects=row['Subjects'],
                                            rois=row['ROI per subject'],
                                            samples=row['Sample points']))
    bubble_size.append(2*np.sqrt(row['Sample points']))

filtered_df['Details'] = hover_text
filtered_df['Size'] = bubble_size

fig3 = go.Figure()

for m in measure_type.keys():
    df_m = filtered_df[filtered_df['Measure'].isin(measure_type[m])]
    fig3.add_trace(go.Scatter(
                    x=df_m['Measure'],
                    y=df_m['R^2'],
                    text='Study: ' + 
                        df_m['Study']+ '<br>' + df_m['Details'],
                    mode='markers',
                    line = dict(color = 'rgba(0,0,0,0)'),
                    marker = dict(color=color_dict[m]),
                    marker_size = df_m['Size'],
                    opacity=0.6,
                    name=m
                    ))
    
fig3.update_layout(
    title = dict(text="Figure 3 - R<sup>2</sup> between MRI and histology across measures "),
    margin=dict(l=0),
    xaxis=dict(title='MRI measure'),
    yaxis=dict(title='R<sup>2</sup>'),
    autosize=False,
    width=800,
    height=500
)

plot(insertLogo(fig3,0.05,0.05,1,-0.25,-0.11,0.052), filename = 'fig3.html',config = config)
display(HTML('fig3.html'))


# To provide a different way to explore sample size and effect size, we also prepared another treemap, where the studies are organised by measures. For each study, the area of its box is proportional to the sample size, while the color represents the related coefficient of determination.
# 
# 
# ```{admonition} Figure 4
# :class: tip
# You can click on each box to expand the related category, and for each study you can find out more details.
# ```

# ### Figure 4

# In[5]:


filtered_df=filtered_df.sort_values(by=['Study','Measure'])

args = dict(data_frame=filtered_df, values='Sample points',
            color='R^2', hover_data='',
            path=['Measure', 'Study'],
            color_continuous_scale='Viridis')
args = px._core.build_dataframe(args, go.Treemap)
treemap_df = px._core.process_dataframe_hierarchy(args)['data_frame']

fig4 = go.Figure(go.Treemap(
        ids=treemap_df['id'].tolist(),
        labels=treemap_df['labels'].tolist(),
        parents=treemap_df['parent'].tolist(),
        values=treemap_df['Sample points'].tolist(),
        branchvalues='total',
        text='R<sup>2</sup>: ' + filtered_df['R^2'].astype(str) + '<br>' + filtered_df['Details'],
        hovertext=filtered_df['Study'] + '<br>R<sup>2</sup>: ' + filtered_df['R^2'].astype(str) +
            '<br>Number of samples: ' + filtered_df['Sample points'].astype(str),
        hoverinfo='text',
        textfont=dict(
            size=15,
        ),
        marker=dict(
            colors=filtered_df['R^2'],
            colorscale='Viridis',
            colorbar=dict(title='R<sup>2</sup>'),
            showscale=True
        )
    )
)

fig4 = fig4.update_layout(
    title=dict(text="Figure 4 - R<sup>2</sup> values across studies"),
    autosize=False,
    width=650,
    height=600,
    margin=dict(
        l=0
    )
)

# Save (pickle) filtered dataframe
# filtered_df.to_pickle('filtered_df.pkl')

plot(insertLogo(fig4,0.04,0.04,1,-0.055,-0.11,0.045), filename = 'fig4.html',config = config)
display(HTML('fig4.html'))


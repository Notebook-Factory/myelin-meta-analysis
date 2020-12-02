#!/usr/bin/env python
# coding: utf-8

# ## Literature overview
# 
# First, how were the studies selected? We used the [Medline database](https://pubmed.ncbi.nlm.nih.gov) and retrieved all the records mentioning (1) myelin, (2) MRI and (3) histology (or a related technique). The full list of keywords is provided in the preprint.
# 
# 
# ```{admonition} Figure 1
# :class: tip
# The Sankey diagram shows the screening procdess. You can hover with the mouse on each block and connection to see details about the number of studies and exclusion criteria.
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


# ### Figure 1

# In[3]:


config={'showLink': False, 'displayModeBar': False}

screening_info = ['Records obtained from the Medline database',
                  'Records obtained from previous reviews',
                  """
                    Exclusion critera:<br>
                    - work relying only on MRI;<br>
                    - work relying only on histology or equivalent approach;<br>
                    - work reporting only qualitative comparisons.
                  """,
                  'Records selected for full-text evaluation',
                  """
                    Exclusion criteria:<br>
                    - studies using MRI-based measures in arbitrary units;<br>
                    - studies using measures of variation in myelin content;<br>
                    - studies using arbitrary assessment scales;<br>
                    - studies comparing absolute measures of myelin with relative measures;<br>
                    - studies reporting other quantitative measures than correlation or R^2 values;<br>
                    - studies comparing histology from one dataset and MRI from a different one.
                  """,
                  'Studies selected for literature overview',
                  """
                    Exclusion criteria:<br>
                     - not providing an indication of both number of subjects and number of ROIs.
                  """]

fig1 = go.Figure(data=[go.Sankey(
    arrangement = "freeform",
    node = dict(
      pad = 80,
      thickness = 10,
      line = dict(color = "black", width = 0.5),
      label = ["Main records identified (database searching)",
               "Additional records (reviews)",
               "Records screened",
               "Records excluded",
               "Full-text articles assessed for eligibility",
               "Full-text articles excluded",
               "Studied included in the literature overview",
               "Studies included in the meta-analysis"],
      x = [0, 0, 0.4, 0.6, 0.5, 0.8, 0.7, 1],
      y = [0, 0, 0.5, 0.8, 0.15, 0.05, 0.4, 0.6],
      hovertemplate = "%{label}<extra>%{value}</extra>",
      color = ["darkblue","darkblue","darkblue","darkred","darkgreen","darkred","darkgreen","darkgreen"]
    ),
    link = dict(
      source = [0, 1, 2, 2, 4, 4, 6],
      target = [2, 2, 3, 4, 5, 6, 7],
      value = [688, 1, 597, 92, 34, 58, 43],
      customdata = screening_info,
      hovertemplate = "%{customdata}",
  ))])

fig1.update_layout(title = dict(text="Figure 1 - Review methodology"),
                   width=650,
                   height=450,
                   font_size=10,
                   margin=dict(l=0))
    
plot(insertLogo(fig1,0.07,0.07,1.1,0,-0.113,0.07), filename = 'fig1.html',config = config)
display(HTML('fig1.html'))


# We identified 58 studies reporting quantitative comparisons between MRI and histology: these included a variety of methodological choices and experimental conditions, in terms of tissue type (brain, spinal cord, peripheral nerve), condition (*in vivo*, *ex vivo*, *in situ*), species (human, animal), pathology model, and many more. A glimpse of these subdivisions is provided in the following treemap.
# 
# ```{admonition} Figure 2
# :class: tip
# You can click on each box to expand the related category, and for each study you can find out more details and the link to the original paper.
# ```

# ### Figure 2

# In[4]:


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

args = dict(data_frame=info, values='Number of studies',
            color='Number of studies', hover_data='',
            path=['Focus', 'Tissue condition', 'Human/animal', 'Condition', 'Study'],
            color_continuous_scale='Viridis')
args = px._core.build_dataframe(args, go.Treemap)
treemap_df = px._core.process_dataframe_hierarchy(args)['data_frame']

fig2 = go.Figure(go.Treemap(
        ids=treemap_df['id'].tolist(),
        labels=treemap_df['labels'].tolist(),
        parents=treemap_df['parent'].tolist(),
        values=treemap_df['Number of studies'].tolist(),
        branchvalues='total',
        text=info['Summary'],
        hoverinfo='label',
        textfont=dict(
            size=15,
        )
    )
)

fig2 = fig2.update_layout(
    autosize=False,
    width=680,
    height=600,
    margin=dict(
        l=0,
        r=0,
        t=0,
        b=45,
    )
)

plot(insertLogo(fig2,0.03,0.03,0.99,-0.02,-0.093,0.03), filename = 'fig2.html',config = config)
display(HTML('fig2.html'))


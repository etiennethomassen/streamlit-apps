import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

# https://github.com/streamlit/streamlit/issues/455
# https://github.com/PablocFonseca/streamlit-aggrid
from st_aggrid import GridOptionsBuilder, AgGrid

"""
# Rotational Forest Management
"""
interest = st.sidebar.slider('Interest rate (0.0% - 10.0%)', min_value=0.0, max_value=10.0, step=.1)

"""
Below you can define a management prescription for a given stand, including associated costs and revenues in order
to analyse the financial performance of the given strategy. In the broadest sense, an asset's value is the net present 
value of satisfactions it yields (Klemperer, 2003). This analysis focuses on the monetary value only.

## Stand prescription
The table below can be adapted by adding, removing and editing measures and the associated costs and revenues.
"""

df = pd.DataFrame(np.arange(0, 101, 5), columns=['t'])
header_list = ['t', 'measure', 'costs', 'revenue']
df = df.reindex(columns=header_list)
df['costs'] = 0
df['revenue'] = 0


df.loc[[0], ['measure', 'costs', 'revenue']] = ['reforest', 100, 0]
df.loc[[2], ['measure', 'costs', 'revenue']] = ['fertilization', 60, 0]
df.loc[[4], ['measure', 'costs', 'revenue']] = ['thinning', 0, 200]
df.loc[[8], ['measure', 'costs', 'revenue']] = ['harvest and land sale', 0, 3300]

gb = GridOptionsBuilder(min_column_width=50, editable_columns=True)
gb.build_columnsDefs_from_dataframe(df)
# gb.enableSideBar()
gridOptions = gb.build()

returned_df = AgGrid(df, gridOptions=gridOptions)
returned_df['result'] = returned_df['revenue'] - returned_df['costs']

returned_df['npv_costs'] = round(returned_df['costs'] / (1 + interest/100)**returned_df['t'], 2)
returned_df['npv_revenue'] = round(returned_df['revenue'] / (1 + interest/100)**returned_df['t'], 2)

returned_df.loc[0, 'npv'] = 0
for i in range(0, len(returned_df)):
    if i == 0:
        returned_df.loc[i, 'npv'] = returned_df.loc[i, 'npv_revenue'] - returned_df.loc[i, 'npv_costs']
    else:
        returned_df.loc[i, 'npv'] = returned_df.loc[i-1, 'npv'] + (returned_df.loc[i, 'npv_revenue'] - returned_df.loc[i, 'npv_costs'])


"""

## Net Present Value

The Net Present Value (NPV) is the maximum willingness to pay for an asset using the buyer's discount rate (Klemperer, 2003).

"""

# add labels just for showing them with
# https://github.com/altair-viz/altair/issues/984#issuecomment-401086680
returned_df['Net Present Value'] = 'NPV'

base = alt.Chart(returned_df).encode(x="t").properties(title=f'Yearly financial result and NPV at {interest}% interest')
bar = base.mark_bar().encode(
    x="t",
    y="result:Q",
    color=alt.condition(
        alt.datum.result > 0,
        alt.value("steelblue"),  # The positive color
        alt.value("orange"),      # The negative color
    )
).properties(width=600)

line = base.mark_line(color='red').encode(
    y='npv:Q',
    opacity='Net Present Value'
)

c = (bar + line).properties(width=600)

st.altair_chart(c, use_container_width=True)


"""
## Literature

Klemperer, W.D. 2003. Forest Resourece Economics and Finance. 551p.
"""

"""
## Calculated table
"""
# clean (remove columns added just for Altair)
returned_df.drop(['Net Present Value'], axis=1, inplace=True)
returned_df

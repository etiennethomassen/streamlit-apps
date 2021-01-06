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

# Settings in the sidebar
st.sidebar.title('Settings')
st.sidebar.markdown('Main settings for the calculations. The actual management prescription can be altered '
                    'in the table in the main body')

st.sidebar.subheader('Rotation length')
# st.sidebar.markdown('Set the interest rate.')

rotation = st.sidebar.slider('Rotation length (10 - 200)', min_value=10, value=70, max_value=200, step=5)
st.sidebar.write('Current rotation length:', rotation, ' years')

st.sidebar.subheader('Interest')
# st.sidebar.markdown('Set the interest rate.')

interest = st.sidebar.slider('Interest rate (0.0% - 10.0%)', min_value=0.0, value=3.0, max_value=10.0, step=.1)
st.sidebar.write('Current interest value:', interest, '%')

st.sidebar.subheader('Additional yearly costs')
# st.sidebar.markdown('Set additional yearly costs.')

yearly_costs = st.sidebar.slider('Additional yearly costs (0 - 200)', min_value=0.0, max_value=200.0, step=1.0)
st.sidebar.write('Additional yearly costs:', yearly_costs)

st.sidebar.subheader('Additional yearly revenues')
# st.sidebar.markdown('Set additional yearly income.')

yearly_revenue = st.sidebar.slider('Additional yearly revenue (0 - 200)', min_value=0.0, max_value=200.0, step=1.0)
st.sidebar.write('Additional yearly revenue:', yearly_revenue)

st.sidebar.markdown('Set additional yearly costs. For example taxation or management overhead.')

st.sidebar.info('CC-BY Etiënne Thomassen')

with st.beta_expander("Edit stand prescription", expanded=True):
    """
    Below you can define a management prescription for a given stand, including associated costs and revenues in order
    to analyse the financial performance of the given strategy. In the broadest sense, an asset's value is the net present 
    value of satisfactions it yields (Klemperer, 1996). This analysis focuses on the monetary value only.
    
    ## Stand prescription
    The table below can be adapted by adding, removing and editing measures and the associated costs and revenues.
    """

    df = pd.DataFrame(np.arange(0, rotation+1, 1), columns=['t'])
    header_list = ['t', 'measure', 'costs', 'revenue']
    df = df.reindex(columns=header_list)
    df['costs'] = 0
    df['revenue'] = 0


    df.loc[[0], ['measure', 'costs', 'revenue']] = ['reforest', 5000, 0]
    df.loc[[10], ['measure', 'costs', 'revenue']] = ['thinning', 65, 355.45]
    df.loc[[15], ['measure', 'costs', 'revenue']] = ['thinning', 65, 1435.13]
    df.loc[[20], ['measure', 'costs', 'revenue']] = ['thinning', 65, 2187.50]
    df.loc[[25], ['measure', 'costs', 'revenue']] = ['thinning', 65, 1983.10]
    df.loc[[30], ['measure', 'costs', 'revenue']] = ['thinning', 65, 2593.94]
    df.loc[[35], ['measure', 'costs', 'revenue']] = ['thinning', 65, 2378.21]
    df.loc[[40], ['measure', 'costs', 'revenue']] = ['thinning', 65, 2613.07]
    df.loc[[45], ['measure', 'costs', 'revenue']] = ['thinning', 65, 2387.76]
    df.loc[[50], ['measure', 'costs', 'revenue']] = ['thinning', 65, 2177.34]
    df.loc[[55], ['measure', 'costs', 'revenue']] = ['thinning', 65, 2348.20]
    df.loc[[60], ['measure', 'costs', 'revenue']] = ['thinning', 65, 2157.30]
    df.loc[[65], ['measure', 'costs', 'revenue']] = ['thinning', 65, 2440.96]
    df.loc[[70], ['measure', 'costs', 'revenue']] = ['harvest and land sale', 65, 42360.34]


    # Klemperer 1996 p227
    # df.loc[[0], ['measure', 'costs', 'revenue']] = ['reforest', 150, 0]
    # df.loc[[10], ['measure', 'costs', 'revenue']] = ['precommercial thinning', 50, 0]
    # df.loc[[20], ['measure', 'costs', 'revenue']] = ['thinning', 0, 300]
    # df.loc[[40], ['measure', 'costs', 'revenue']] = ['harvest and land sale', 0, 3500]

    # Bullard & Straka 2011. Basic Concepts in Forest Valuation and Investment Analysis Basic Concepts in Forest Valuation and Investment Analysis
    # Section 4. Financial criteria – page 4.20
    # df.loc[[0], ['measure', 'costs', 'revenue']] = ['reforest', 95, 0]
    # df.loc[[15], ['measure', 'costs', 'revenue']] = ['precommercial thinning', 0, 550]
    # df.loc[[25], ['measure', 'costs', 'revenue']] = ['thinning', 0, 1500]
    # df.loc[[35], ['measure', 'costs', 'revenue']] = ['harvest and land sale', 0, 3350]

    gb = GridOptionsBuilder(min_column_width=50, editable_columns=True)
    gb.build_columnsDefs_from_dataframe(df)
    # gb.enableSideBar()
    gridOptions = gb.build()

    returned_df = AgGrid(df, gridOptions=gridOptions)

    # TODO double use triggers copy warning
    returned_df['costs_yearly'] = 0
    returned_df['costs_yearly'][1:] = yearly_costs
    returned_df['revenue_yearly'] = 0
    returned_df['revenue_yearly'][1:] = yearly_revenue

    # Set initial result
    returned_df['result'] = returned_df['revenue'] + returned_df['revenue_yearly'] \
                            - returned_df['costs'] - returned_df['costs_yearly']

    returned_df['npv_costs'] = round((returned_df['costs'] + returned_df['costs_yearly']) / (1 + interest / 100) ** returned_df['t'], 2)
    returned_df['npv_revenue'] = round((returned_df['revenue'] + returned_df['revenue_yearly']) / (1 + interest / 100) ** returned_df['t'], 2)

    # calculate FPV per cost and revenue
    returned_df['fpv_costs'] = round((returned_df['costs'] + returned_df['costs_yearly']) * (1 + interest / 100) ** (rotation - returned_df['t']), 2)
    returned_df['fpv_revenue'] = round((returned_df['revenue'] + returned_df['revenue_yearly']) * (1 + interest / 100) ** (rotation - returned_df['t']), 2)

    # calculate NPV per year
    returned_df.loc[0, 'npv'] = 0
    for i in range(0, len(returned_df)):
        if i == 0:
            returned_df.loc[i, 'npv'] = returned_df.loc[i, 'npv_revenue'] - returned_df.loc[i, 'npv_costs']
        else:
            returned_df.loc[i, 'npv'] = returned_df.loc[i - 1, 'npv'] + (
                        returned_df.loc[i, 'npv_revenue'] - returned_df.loc[i, 'npv_costs'])

    # calculate FPV per year
    returned_df.loc[0, 'fpv'] = 0
    for i in range(0, len(returned_df)):
        if i == 0:
            returned_df.loc[i, 'fpv'] = returned_df.loc[i, 'fpv_revenue'] - returned_df.loc[i, 'fpv_costs']
        else:
            returned_df.loc[i, 'fpv'] = returned_df.loc[i - 1, 'fpv'] + (
                        returned_df.loc[i, 'fpv_revenue'] - returned_df.loc[i, 'fpv_costs'])

    # calculate LEV
    filled_df = returned_df[returned_df['result'] > 0]
    result = filled_df[filled_df['t'] == filled_df['t'].max()]
    fpv_cumulative = result.iloc[0]['fpv']
    npv_cumulative = result.iloc[0]['npv']

    lev = fpv_cumulative / ((1 + interest / 100) ** rotation - 1)

st.subheader('Net Present Value @ ' + str(interest) + '% interest')
"""
The Net Present Value (NPV) is the maximum willingness to pay for an asset using the buyer's discount rate (Klemperer, 1996).
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
        alt.value("orange"),  # The negative color
    )
).properties(width=600)

line = base.mark_line(color='red').encode(
    y='npv:Q',
    opacity='Net Present Value'
)

c = (bar + line).properties(width=600)

st.altair_chart(c, use_container_width=True)

st.write('Net Present Value (NPV): ', round(npv_cumulative, 2))
st.write('Future Present Value (FPV): ', round(fpv_cumulative, 2))

# Land Expectation Value
st.subheader('Land Expectation Value')
"""
Assuming only the cash flows in the equation, LEV is the maximum an investor could pay for bare land 
and still earn the minimum acceptable rate of return r (Klemperer, 1996).
"""
st.write('Land Expectation Value (LEV): ', round(lev, 2))

st.write('If you purchase the timberland for', round(lev, 2), ' per unit area and experience the costs '
         'and revenues projected your timberland investment will earn a 9% rate of return (Bullard & Straka 2011)')

"""
## Literature

- Klemperer, W.D. 1996. Forest Resourece Economics and Finance. 551p.
- Bullard, S.H. & T.J. Straka 2011. Basic Concepts in Forest Valuation and Investment Analysis. eBooks. 21. 
https://scholarworks.sfasu.edu/ebooks/21/
"""

# st.subheader('Calculated table')
# clean (remove columns added just for Altair)
# returned_df.drop(['Net Present Value'], axis=1, inplace=True)
returned_df

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from statistics import mode
import pandas as pd
import plotly.express as px

# 2. Create a Dash app instance
app = dash.Dash(
    external_stylesheets=[dbc.themes.JOURNAL],
    name='Tech Layoffs 2020-2022'
    )

app.title = 'Tech Layoffs 2020-2022'

## Navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
    ],
    brand="Tech Layoffs Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)

#Import data untuk dashboard
df = pd.read_csv(r'C:\Users\edgar.manzo\Desktop\training dadp\capstone\data input\layoffs_1.csv')
df['date']= pd.to_datetime(df['date'])
df['bulan']= df['date'].dt.to_period('M')
df['bulan']= df['bulan'].dt.to_timestamp()
df['status'] = ['Publicly traded' if x =='IPO' else 'Privately owned' for x in df['stage']]
most_updated_date = df['date'].max()
## Card Content
total_companies = [
    dbc.CardHeader('Number of Companies'),
    dbc.CardBody([
        html.H1(df['company'].nunique())
    ]),
]

total_laid_off = [
    dbc.CardHeader('Number of People laid off'),
    dbc.CardBody([
        html.H1(df['total_laid_off'].sum())
    ]),
]

data_terbaru = [
    dbc.CardHeader('Latest entry'),
    dbc.CardBody([
        html.H1(f"{most_updated_date.strftime('%A')}, {most_updated_date.strftime('%d')} {most_updated_date.strftime('%b')} {most_updated_date.strftime('%Y')}")
    ])
]


#Area Plot


group = pd.pivot_table(df, index='bulan', values='total_laid_off', aggfunc='sum').reset_index()

area_plot = px.area(group, 
        x='bulan', 
        y='total_laid_off', 
        labels= {'bulan': 'Month', 'total_laid_off':'Number of people laid off'},
       template= 'ggplot2',
       title='Number of People Laid Off in Months')


# Pie plot


status = pd.pivot_table(df, 
                            index='status', 
                            values='total_laid_off', 
                            aggfunc='sum').sort_values('total_laid_off',ascending=False).reset_index()
pie_plot = px.pie(status.sort_values('total_laid_off', ascending=True), 
       values='total_laid_off', 
       names='status',
      title=f"Most layoffs came from {str(status['status'].head(1)[0])} companies",
      template='ggplot2')
pie_plot.update_traces(hovertemplate='<b>%{value}</b> employees have been laid off from <b>%{label}</b> companies',
textinfo='label+percent')

# Bar plot 1


industry = pd.pivot_table(df, 
                            index='industry', 
                            values='total_laid_off', 
                            aggfunc='sum').sort_values('total_laid_off',ascending=False).reset_index().head(10)
bar_1 = px.bar(industry.sort_values('total_laid_off', ascending=True), 
       x='total_laid_off', 
       y='industry',
      title='Top 10 Industry with most layoffs',
      template='ggplot2',
      labels= {'industry': 'Industry', 'total_laid_off':'Number of people laid off'})

#Bar plot 2


perusahaan = pd.pivot_table(df, 
                            index='company', 
                            values='total_laid_off', 
                            aggfunc='sum').sort_values('total_laid_off',ascending=False).reset_index().head(10)
bar_2 = px.bar(perusahaan.sort_values('total_laid_off', ascending=True), 
       x='total_laid_off', 
       y='company',
      title='Top 10 Company with most layoffs',
      template='ggplot2',
      labels= {'company': 'Company', 'total_laid_off':'Number of people laid off'})

# bar plot 3


lokasi = pd.pivot_table(df, 
                            index='location', 
                            values='total_laid_off', 
                            aggfunc='sum').sort_values('total_laid_off',ascending=False).reset_index().head(10)
bar_3 = px.bar(lokasi.sort_values('total_laid_off', ascending=True), 
       x='total_laid_off', 
       y='location',
      title='Top 10 cities with most layoffs',
      template='ggplot2',
      labels= {'location': 'City', 'total_laid_off':'Number of people laid off'})


# scatter plot


sketer = px.scatter(df[(df['total_laid_off'] != 0) & (df['funds_raised'] != 0)], 'funds_raised', 'total_laid_off',
          template='ggplot2', log_x=True, hover_data=['company'],
          title = 'There is a positive, albeit weak correlation between log of funds raised by companies and number of people laid off',
          labels= {'funds_raised': 'Log(funds raised)', 'total_laid_off':'Number of people laid off'})
sketer.update_traces(hovertemplate='% company have laid off %{y} employees have raised <b>%{x}</b> Mio USD')


#### Layout

app.layout = html.Div([
    navbar,

    html.Br(),

    # Component main page

    html.Div([ 
        ## Row 1  
        dbc.Row(
            [
            ### Column 1
            dbc.Col(
                [
                    dbc.Card(total_companies, color='white'),
                    html.Br(),
                    dbc.Card(total_laid_off, color='blue'),
                    html.Br(),
                    dbc.Card(data_terbaru, color='turquoise'),
                ],
                width=2),

            ### Column 2
            dbc.Col([
                dcc.Graph(figure=area_plot),
            ], width=5),
            
            dbc.Col([dcc.Graph(figure=sketer)],
            width=5),

            ]
        ),

        html.Hr(),

        ## Row 2
        dbc.Row(
            [
            ### Column 1
            dbc.Col([
                html.H1('Top 10 Rank'),
                dbc.Card([
                    dbc.CardHeader('Select Country'),
                    dbc.CardBody(
                        dcc.Dropdown(
                            id='choose_country',
                            options=df['country'].unique(),
                            value='All'
                        ),
                    ),
                ]),
                dbc.Tabs([
                    #TAB 1 : Ranking by country
                    dbc.Tab(
                        dcc.Graph(figure = bar_1,
                            id='bar_1'
                        ),  
                        label='By Industry'),

                    #TAB 2: Ranking by industry
                    dbc.Tab(
                        dcc.Graph(figure = bar_2,
                            id='bar_2',
                        ), 
                        label='By Company'),

                    dbc.Tab(
                        dcc.Graph(figure = bar_3,
                            id='bar_3',
                        ), 
                        label='By Location'),
                ]),
            ], width=6),

            ### Column 2
            dbc.Col([
                html.H1('Proportion'),
                dcc.Graph(figure = pie_plot,
                    id='pie_plot',
                ),
            ],
                
                width=6),
            
            ]
        )
    ], style={
        'paddingLeft':'30px',
        'paddingRight':'30px'
    }), 

])

# ### Callback plot ranking
# @app.callback(
#     Output(component_id='plotranking', component_property='figure'),
#     Input(component_id='choose_country', component_property='value')
# )

# def update_plotrank(country_name):
#     gpp_indo = gpp[gpp['country_long']== country_name]

#     top_indo = gpp_indo.sort_values('capacity in MW').tail(10)

# # Visualize
#     plot_ranking = px.bar(
#     top_indo,
#     x = 'capacity in MW',
#     y = 'name of powerplant',
#     template = 'ggplot2',
#     title = f'Ranking of Overall Power Plants in {str(country_name)}'
# )
#     return plot_ranking


# ### Callback plot distribution
# @app.callback(
#     Output(component_id='plotdistribution', component_property='figure'),
#     Input(component_id='choose_country', component_property='value')
# )

# def update_plotdist(country_name):
#     gpp_indo = gpp[gpp['country_long']== country_name]

#     plot_distribution = px.box(
#     gpp_indo,
#     color='primary_fuel',
#     y='capacity in MW',
#     template='ggplot2',
#     title='Distribution of capacity in MW in each fuel',
#     labels={
#         'primary_fuel': 'Type of Fuel'
#     }
#     ).update_xaxes(visible=False)
#     return plot_distribution

# ### Callback pie chart
# @app.callback(
#     Output(component_id='plotpie', component_property='figure'),
#     Input(component_id='choose_country', component_property='value')
# )

# def update_pie(country_name):
#     gpp_indo = gpp[gpp['country_long']== country_name]

#     # aggregation
#     agg2=pd.crosstab(
#     index=gpp_indo['primary_fuel'],
#     columns='No of Power Plant'
#     ).reset_index()

#     # visualize
#     plot_pie = px.pie(
#     agg2,
#     values='No of Power Plant',
#     names='primary_fuel',
#     color_discrete_sequence=['aquamarine', 'salmon', 'plum', 'grey', 'slateblue'],
#     template='ggplot2',
#     hole=0.4,
#     title = f'Proportion of Overall Power Plants primary fuel in {str(country_name)}',
#     labels={
#         'primary_fuel': 'Type of Fuel'
#     }
#     )
#     return plot_pie


# 3. Start the Dash server
if __name__ == "__main__":
    app.run_server()
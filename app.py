from dash import Dash,dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import datetime

# import the data and name the header
data = pd.read_csv('/Users/ciciling/Downloads/SN_m_tot_V2.0.csv',
                   names=["Year", "Month", "Date", "Mean_Number","S.D.","observations","marker"],delimiter=';')

# create dictionary for real time image
real_time = {'EIT 171': 'https://soho.nascom.nasa.gov/data/realtime/eit_171/512/latest.jpg',
             'EIT 195': 'https://soho.nascom.nasa.gov/data/realtime/eit_195/512/latest.jpg',
             'EIT 284':'https://soho.nascom.nasa.gov/data/realtime/eit_284/512/latest.jpg',
             'EIT304':'https://soho.nascom.nasa.gov/data/realtime/eit_304/512/latest.jpg',
             'SDO/HMI Magnetogram':'https://soho.nascom.nasa.gov/data/realtime/hmi_mag/512/latest.jpg',
             'LASCO C2':'https://soho.nascom.nasa.gov/data/realtime/c2/512/latest.jpg',
             'LASCO C3':'https://soho.nascom.nasa.gov/data/realtime/c3/512/latest.jpg',
             'MDI Continuum': 'https://soho.nascom.nasa.gov/data/realtime/hmi_igr/1024/latest.jpg'
            }

# build an app
app = Dash(__name__)

server = app.server
# define the dashboard layout
app.layout = html.Div([
        # put section title on first graph
        html.H4('Sunspot visualizations',style={'font-size': '27px', 'textAlign': 'center'}),
        # create the graph object
        dcc.Graph(id="graph", style={'width':'70vw', 'height':'60vh'}),

        # create the rangeslider to select certain years
        html.P("Select Year Range:"),
        dcc.RangeSlider(data['Year'].min(), data['Year'].max(), marks=None, value=[1749, 2020], id='year_range'),
        # report back to user the year they have chosen
        html.Div(id='output-container-range-slider', style={'textAlign': 'center', 'fontWeight': 'bold'}),

        # create observation periods selection slider
        html.P("Select the number of observation periods to get a smoothing line:"),
        dcc.Slider(id='number_mean', min=0, max=24, step=1, value=1),


        # put section title on second graph
        html.H4('Variability of Sunspot Cycle', style={'font-size': '27px', 'textAlign': 'center'}),
        # create the graph object
        dcc.Graph(id="scatter",style={'width':'50vw', 'height':'80vh'}),
        # slider to select cycle periods
        html.P("Select cycle period:"),
        dcc.Slider(id='cycle_year', min=1, max=20, step=1, value=11),

        # put section title on the image
        html.H4('Real time image of the sun', style={'font-size': '27px', 'textAlign': 'center'}),
        # select desired image filter
        dcc.Dropdown(id='image_filter', options=sorted(list(set(real_time.keys()))),
                     value = 'MDI Continuum', clearable = False),
        # import realtime image from outside pathway
        html.Img(id = 'image_display', width = '35%'),
        # show the user the time the image is last retrieved
        html.P('Last updated ' + str(datetime.datetime.now())),
        # refresh most current image
        html.A(html.Button('Refresh real time image'),href='/')
])

# the callback and function for the first graph
@app.callback(
    Output("graph", "figure"),
    Output('output-container-range-slider', 'children'),
    Input("year_range", "value"),
    Input("number_mean", "value")
)

def display_graph(year_range,number_mean):
    # limit the data to only selected range of years
    selected_df = data[(data['Year'] >= year_range[0]) & (data['Year'] <= year_range[1])]
    # create the figure
    fig = go.Figure()
    # add monthly sunspot mean visualization
    fig.add_trace(go.Scatter(x=selected_df['Date'], y=selected_df['Mean_Number'],
                             mode='lines',
                             name='monthly'))

    # create columns in the dataframe for smoothed data
    selected_df['smoothing'] = selected_df['Mean_Number'].rolling(number_mean).mean()
    # add smoothing line to the graph
    fig.add_trace(go.Scatter(x=selected_df['Date'], y=selected_df['smoothing'],
                             mode='lines',
                             name='smoothed'))
    fig.update_layout(title='Sunspot monthly mean and smoothed line',
                      xaxis_title='Time(years)',
                      yaxis_title='Sunspot mean',
                      paper_bgcolor='#95D6E1')
    # return the graph and also the range the user selected
    return fig, 'You have selected {} to {}'.format(year_range[0],year_range[1])


# the callback and function for the second graph
@app.callback(
    Output('scatter', 'figure'),
    Input('cycle_year', 'value')
)
def display_scatter(cycle_year):
    # create new dataframe for second visualizations
    sunspot_df = data
    sunspot_df.dropna()

    # create the figure
    fig2 = go.Figure()

    # add new columns to the dataset to seperate years to cycles
    sunspot_df['Cycle_Length'] = sunspot_df['Date'] % cycle_year
    fig2.add_trace(go.Scatter(x=sunspot_df['Cycle_Length'], y=sunspot_df['Mean_Number'],
                             mode='markers'))
    fig2.update_layout(title='Sunspot Variation',
                       xaxis_title='Years',
                       yaxis_title='# of Sunspot',
                       paper_bgcolor='#95D6E1')
    return fig2

# the callback and function for the third image
@app.callback(
    Output('image_display', 'src'),
    Input('image_filter', 'value')
)

def image_filter(image_filter):
    # return the according source for selected image filter
    source = real_time[image_filter]
    return source

app.run_server(debug=True)

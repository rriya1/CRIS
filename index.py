import dash
import dash_daq as daq
from dash import dcc, html,Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO 
from datetime import date
import pandas as pd
import plotly.express as px
import numpy as np

#======================================working with data====================================================#

cris_df=pd.read_csv("E:\RIYA_PERSONAL\CS\CRIS\Railway_Expenditure_Analysis_FINAL_ONLY\index_data_csv")

unique_finyears = cris_df['FINYEAR'].unique()
unique_finyears.sort()

unique_demand=cris_df['DEMAND'].unique()
unique_demand.sort()

unique_railways = cris_df.drop_duplicates(subset=['RLYCODE', 'RailwayName'])
unique_railways = unique_railways.sort_values(by='RLYCODE')
default_railway = cris_df['RLYCODE'].value_counts().idxmax() #railway which occurs maximum number of times

cris_df['AU'] = cris_df['AU'].astype(str).str.zfill(4)
unique_au=cris_df.drop_duplicates(subset="AU")
unique_au = unique_au.sort_values(by='AU')

cris_df['START_YEAR'] = pd.to_datetime(cris_df['START_YEAR'], format='%Y')
cris_df['END_YEAR'] = pd.to_datetime(cris_df['END_YEAR'], format='%Y')

cris_df['ACCYEARMONTH'] = pd.to_datetime(cris_df['ACCYEARMONTH'], errors='coerce')

# Create 'EXPENDITURE' column
cris_df['EXPENDITURE'] = np.where(cris_df['DATA_TYPE'] == 'EXP', cris_df['AMOUNT'], 0)
# Create 'BUDGET' column
cris_df['BUDGET'] = np.where(cris_df['DATA_TYPE'] == 'BUD', cris_df['AMOUNT'], 0)


sum_data = cris_df.groupby(['RLYCODE', 'ACCYEARMONTH', 'RailwayName', 'AU', 'AUName'])['EXPENDITURE'].sum().reset_index()


#=========================================using morph theme==========================================

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MORPH],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

#============================================Components====================================================#

# offcanvas sidebar 
offcanvas = html.Div(
    [
        dbc.Button(
            "Page",
            id="open-offcanvas-scrollable",
            n_clicks=0, className="btn btn-primary btn-sm"
        ),
        dbc.Offcanvas(
            html.P("Available Pages"),
            id="offcanvas-scrollable",
            scrollable=True,
            title="Railway Expenditure Analysis",
            is_open=False,
        ),
    ]
)

#theme switch toggler
themetoggle=daq.ToggleSwitch(
        id='theme_toggle',
        value=False
    )

#sticky heading
heading=html.Div(
    [
        dbc.Row(
            [
                dbc.Col(offcanvas,width=1, style={ "margin-top":13}),
                dbc.Col([html.H1("Railway Expenditure Analysis")],width=10, className="text-center"),
                dbc.Col(themetoggle,width=1,style={"margin-top":13}),
                
            ],className="head1light"),
        dbc.Row(
            [
                dbc.Col(html.H6("Analyzing Financial Data for Different Zones and Sub-divisions"),className="text-center", style={"margin-top":5})
            ],className="head2light"
        )
    ], style={"sticky":"top", "fixed": True}
)


#to select the graph
dropdown_graph= dbc.Select(
                    options=[
                        {"label":"Expenditure", "value":1},
                        {"label":"Expenditure vs Bugdet", "value":2}
                    ],className="form-select-sm",value=1,id="graph"
                )
#to select the type of graph
dropdown_graph_type= dbc.Select(
                    options=[
                        {"label":"Bar", "value":1},
                        {"label":"Line", "value":2}
                    ],className="form-select-sm",value=1,id="graph_type"
                )
#to select the railway
dropdown_railway= dbc.Select(
                    options=[
                        {"label":"ALL","value":-1},
                        *({"label": f"{railway_code} - {railway_name}", "value": railway_code}
                        for railway_code, railway_name in zip(unique_railways['RLYCODE'], unique_railways['RailwayName']))
                    ],className="form-select-sm",value=default_railway,id="rlycode"
                )
#display only  the AU in the selected railway
dropdown_au= dbc.Select(className="form-select-sm",id="au",value=0000)
#display the unique demands
dropdown_demand= dbc.Select(
                    options=[
                        {"label":"ALL DEMAND", "value":00},
                        *({"label":demand, "value":demand}
                        for demand in unique_demand)
                    ],className="form-select-sm",value=unique_demand[0],id="demand"
                )
#dropdown to select the start year
dropdown_year_start= dbc.Select(
                    options=[
                        {"label":year, "value":year}
                        for year in unique_finyears
                    ],className="form-select-sm",value=unique_finyears[0],id="start_date"
                )
#dropdown to select the end date
dropdown_year_end= dbc.Select(
                    options=[
                        {"label":year, "value":year}
                        for year in unique_finyears
                    ],className="form-select-sm",value=unique_finyears[0],id="end_date"
                )
x_axis_type=dbc.Select(
    options=[
        {"label":"Railway","value":1},
        {"label":"AU","value":2},
        {"label":"Demand","value":3}
    ],id="xaxis",className="form-select-sm",value=1
)

selection=html.Div(
    dbc.Row(
        [
            dbc.Col([
                dbc.Row([
                    dbc.Col(html.H6("Graph: "),width=3),
                    dbc.Col(dropdown_graph)
                ],style={"margin-top":10}),
                dbc.Row([
                    dbc.Col(html.H6("Graph Type: "),width=3),
                    dbc.Col(dropdown_graph_type)
                ],style={"margin-top":5}),
                dbc.Row([
                    dbc.Col(html.H6("X-axis: "),width=3),
                    dbc.Col(x_axis_type)
                ],style={"margin-top":5}),
            ],className="dropcol"),


            dbc.Col([
                dbc.Row([
                    dbc.Col(html.H6("Railway: "),width=3),
                    dbc.Col(dropdown_railway)
                ],style={"margin-top":10}),
                dbc.Row([
                    dbc.Col(html.H6("AU: "),width=3),
                    dbc.Col(dropdown_au)
                ],style={"margin-top":5}),
                dbc.Row([
                    dbc.Col(html.H6("Demand: "),width=3),
                    dbc.Col(dropdown_demand)
                ],style={"margin-top":5}),
            ],className="dropcol"),


            dbc.Col([
                dbc.Row([
                    dbc.Col(html.H6("Start Year: "),width=3),
                    dbc.Col(dropdown_year_start)
                ],style={"margin-top":10}),
                dbc.Row([
                    dbc.Col(html.H6("End Year: "),width=3),
                    dbc.Col(dropdown_year_end)
                ],style={"margin-top":5}),
            ],className="dropcol"),

        ],style={"margin-top":10}
    )
)

#graph area
graph_area=html.Div(
    dbc.Row(
        dbc.Col(
            dcc.Graph(id="graph_visual")
        ),style={"margin-top":30}
    )
)

graph_and_map=html.Div(
    dbc.Row([
        dbc.Col(graph_area,width=9),
        dbc.Col()
    ])
)


#=============================================App Layout=======================================================#

app.layout=dbc.Container([
    heading,
    selection,
    graph_and_map
],fluid=True)

#===============================================Callback========================================================#

#to see the status of the menu bar
@app.callback(
    Output("offcanvas-scrollable", "is_open"),
    Input("open-offcanvas-scrollable", "n_clicks"),
    State("offcanvas-scrollable", "is_open"),
)
def toggle_offcanvas_scrollable(n1, is_open):
    if n1:
        return not is_open
    return is_open

#to remove line when exp vs budget is selected
@app.callback(
    Output("graph_type", "options"),
    Input("graph", "value")
)
def update_graph_type_options(graph_value):
    graph_value=int(graph_value)
    if graph_value == 2:
        options = [
            {"label": "Bar", "value": 1}
        ]
    else:
        options = [
            {"label": "Bar", "value": 1},
            {"label": "Line", "value": 2}
        ]
    return options

#to make the end date disable in some cases
@app.callback(
    Output("start_date", "disabled"),
    Output("end_date", "disabled"),
    Input("graph", "value"),
    Input("graph_type", "value")
)
def disable_fin_year_dropdown(graph_value, graph_type_value):
    graph_value=int(graph_value)
    graph_type_value=int(graph_type_value)
    if graph_value==1 and graph_type_value==1:
        return False, False
    else:
        return False, True

#to display the AU's of selected railway only
@app.callback(
        Output('au','options'),
        Input('rlycode','value')
)
def audropdown(rlycode):
    rlycode=int(rlycode)
    if rlycode==-1:
        return [{"label":"ALL AU in Railway","value":0000}]
    selected_rlycode=cris_df[cris_df['RLYCODE']==rlycode]
    drop_aus = selected_rlycode.drop_duplicates(subset=['AU', 'AUName'])
    drop_aus=drop_aus.sort_values(by="AU")
    options=[
        {"label":"ALL AU","value":0000},
        *({"label":f"{au_code}-{au_name}","value":au_code}
        for au_code,au_name in zip(drop_aus['AU'],drop_aus['AUName']))
    ]
    return options

#to change the value of enddate according to startdate
@app.callback(
    Output("end_date", "options"),
    Input("start_date", "value")
)
def update_end_date_options(start_date):
    filtered_years = unique_finyears[unique_finyears >= start_date]
    end_date_options = [
        {"label": year, "value": year}
        for year in filtered_years
    ]

    return end_date_options

# #to make a graph
@app.callback(
    Output("graph_visual","figure"),
    Input("graph","value"),
    Input("graph_type","value"),
    Input("xaxis","value"),
    Input("rlycode","value"),
    Input("au","value"),
    Input("demand","value"),
    Input("start_date","value"),
    Input("end_date","value")
)
def update_fig(graph,graph_type,xaxis,rlycode,au,demand,start,end):
    #coverting to correct format
    graph=int(graph)
    graph_type=int(graph_type)
    xaxis=int(xaxis)
    rlycode=int(rlycode)
    #au=int(au)
    demand=int(demand)
    start=str(start)
    start= start.split('-')[0] 
    start = pd.to_datetime(start, format='%Y')

    if graph_type==2 and graph==1:
        fig=expenditure_line(xaxis,rlycode,au,demand,start)
        return fig
    if graph==2:
        fig=exp_vs_budget_bar(xaxis,rlycode,au,demand,start)
        return fig
    if graph==1 and graph_type==1:
        #only avaialable for exp bar graph
        end=str(end)
        end = end.split('-')[1] 
        end= pd.to_datetime(end, format='%Y')
        fig=expenditure_bar(xaxis,rlycode,au,demand,start,end)
        return fig
#============================functions that callback will use to make graph=================================#
#correct function
def exp_vs_budget_bar(xaxis, rlycode, au, demand, start):
    global cris_df
    data = cris_df

    if rlycode != -1:
        data = data[data['RLYCODE'] == rlycode]
        if au != str(0000):
            print(au)
            print(type(au))
            data = data[data['AU'] == au]
        print(data)
    if demand != 00:
        data = data[data['DEMAND'] == demand]
    data = data[data['START_YEAR'] >= start]
    
    if xaxis == 1:
        # Group by 'RLYCODE' and calculate the sum of 'EXPENDITURE' and 'BUDGET'
        sum_data = data.groupby('RLYCODE').agg({
            'EXPENDITURE': 'sum',
            'BUDGET': 'sum'
        }).reset_index()
        rlycode_to_rlyname = dict(zip(data['RLYCODE'], data['RailwayName']))
        # Create the stacked bar chart
        fig = px.bar(sum_data, x='RLYCODE', y=['EXPENDITURE', 'BUDGET'],
                     title='Expenditure vs Budget by Railway')

        # Update x-axis labels with 'RailwayName'
        fig.update_xaxes(type='category', 
        tickvals=list(rlycode_to_rlyname.keys()),
        ticktext=list(rlycode_to_rlyname.values()))
        return fig
    
    if xaxis==2:
        sum_data = data.groupby('AU').agg({
            'EXPENDITURE': 'sum',
            'BUDGET': 'sum'
        }).reset_index()
        print(sum_data)
        au_to_auname = dict(zip(data['AU'], data['AUName']))
        fig = px.bar(sum_data, x='AU', y=['EXPENDITURE', 'BUDGET'],
                     title='Expenditure vs Budget by AU')
        fig.update_xaxes(type='category', 
        tickvals=list(au_to_auname.keys()),
        ticktext=list(au_to_auname.values()))
        return fig

    if xaxis==3:
        sum_data = data.groupby('DEMAND').agg({
            'EXPENDITURE': 'sum',
            'BUDGET': 'sum'
        }).reset_index()
        print(sum_data)
        fig = px.bar(sum_data, x='DEMAND', y=['EXPENDITURE', 'BUDGET'],
                     title='Expenditure vs Budget by Demand')
        fig.update_xaxes(type='category', 
        tickvals=sum_data['DEMAND'], ticktext=sum_data['DEMAND'])
        return fig

def expenditure_bar(xaxis,rlycode,au,demand,start,end):
    global cris_df
    data = cris_df
    print(type(end))
    print(type(start))
    if rlycode != -1:
        data = data[data['RLYCODE'] == rlycode]
        if au != str(0000):
            data = data[data['AU'] == au]
    if demand != 00:
        data = data[data['DEMAND'] == demand]
    data = data[data['START_YEAR'] >= start]
    data = data[data['END_YEAR'] <= end]

    if xaxis == 1:
        # Group by 'RLYCODE' and calculate the sum of 'EXPENDITURE' and 'BUDGET'
        sum_data = data.groupby('RLYCODE').agg({
            'EXPENDITURE': 'sum'
        }).reset_index()
        rlycode_to_rlyname = dict(zip(data['RLYCODE'], data['RailwayName']))
        # Create the stacked bar chart
        fig = px.bar(sum_data, x='RLYCODE', y='EXPENDITURE',
                     title='Expenditure by Railway')

        # Update x-axis labels with 'RailwayName'
        fig.update_xaxes(type='category', 
        tickvals=list(rlycode_to_rlyname.keys()),
        ticktext=list(rlycode_to_rlyname.values()))
        return fig
    
    if xaxis==2:
        sum_data = data.groupby('AU').agg({
            'EXPENDITURE': 'sum'
        }).reset_index()
        print(sum_data)
        au_to_auname = dict(zip(data['AU'], data['AUName']))
        fig = px.bar(sum_data, x='AU', y='EXPENDITURE',
                     title='Expenditure by AU')
        fig.update_xaxes(type='category', 
        tickvals=list(au_to_auname.keys()),
        ticktext=list(au_to_auname.values()))
        return fig

    if xaxis==3:
        sum_data = data.groupby('DEMAND').agg({
            'EXPENDITURE': 'sum'
        }).reset_index()
        print(sum_data)
        fig = px.bar(sum_data, x='DEMAND', y='EXPENDITURE',
                     title='Expenditure by Demand')
        fig.update_xaxes(type='category', 
        tickvals=sum_data['DEMAND'], ticktext=sum_data['DEMAND'])
        return fig

def expenditure_line(xaxis,rlycode,au,demand,start):
    global cris_df
    data = cris_df
    print(type(start))
    if rlycode != -1:
        data = data[data['RLYCODE'] == rlycode]
        if au != str(0000):
            data = data[data['AU'] == au]
    if demand != 00:
        data = data[data['DEMAND'] == demand]
    data = data[data['START_YEAR'] == start]
    print(type(cris_df['ACCYEARMONTH']))
    data = data.sort_values(by='ACCYEARMONTH', key=lambda x: x.dt.month, ascending=True)
    sum_data = data.groupby(['RLYCODE', 'ACCYEARMONTH', 'RailwayName', 'AU', 'AUName','DEMAND'])['EXPENDITURE'].sum().reset_index()
    if xaxis == 1:
        fig = px.line(sum_data, x="ACCYEARMONTH", y="EXPENDITURE", color='RailwayName')
        return fig
    if xaxis == 2:
        fig = px.line(sum_data, x="ACCYEARMONTH", y="EXPENDITURE", color='AUName')
        return fig
    if xaxis == 3:
        fig = px.line(sum_data, x="ACCYEARMONTH", y="EXPENDITURE", color='DEMAND')
        return fig
    
#=================================================start-app=================================================#

if __name__=='__main__':
    app.run_server(debug=True, port=3000)
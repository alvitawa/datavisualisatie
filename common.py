from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go
import math
from sklearn import datasets, linear_model
import pandas as pd
import numpy as np
import json

# Start notebook mode
init_notebook_mode(connected=True)

times = pd.read_csv("timesData.csv")

def convert_for_intstudent(dataframe):
    # Strips the '=' character from the world_rank column 
    # and removes all entries with NaN values in Interernation_students column
    dataframe['world_rank'] = dataframe['world_rank'].map(lambda x: x.lstrip('='))
    dataframe = dataframe.dropna(axis=0, subset=['international_students'])

    #Make all possible columns datatype integers so you can make calculations with the values
    #Also removed all percentages for easier calculations
    dataframe = dataframe[~times.world_rank.str.contains("-")]
    dataframe = dataframe.apply(pd.to_numeric, errors='ignore')
    
    dataframe['international_students'] = dataframe['international_students'].str[:-1].astype(float)

    dataframe.loc[times['international'] == '-', 'international'] = 0
    dataframe['international'] = dataframe['international'].astype(float)
    
    return dataframe;

converted_intstudent = convert_for_intstudent(times)


def conv_ranking(x):
    spl = x.split('-')
    if len(spl) == 2:
        return (float(spl[0]) + float(spl[1])) / 2
    s = (x if x[0] != '=' else x[1:])
    f = float(s)
    return f

def conv_other(x):
    try:
        return float(x)
    except Exception:
        return 50

mx = dict()
def conv_unit(rw):
    rnk, yr = rw
    dv = mx[yr] if yr in mx else times.loc[times['year'] == yr]['world_rank'].max()
    mx[yr] = dv
    return 100 * (1 - (rnk / dv))
    
times['world_rank'] = times['world_rank'].map(conv_ranking)
times['percentile'] = times[['world_rank', 'year']].apply(conv_unit, axis=1)
country_stats = times[['year', 'country', 'world_rank', 'percentile']].groupby(['year', 'country']).mean()
counts = times.groupby(['year', 'country']).size()
country_stats['count'] = counts

# This function takes in a year as a parameter and filters the complete dataframe on that year
# After that it calculates the mean of the international students per group of 50 universities in the ranking
# The function returns a list with the all the means of the given year. This list is rounded up to a decimal 
def get_meantop200(year, column):
    selected = converted_intstudent[(converted_intstudent['year']) == year][:200]
    means = [selected[column][:50].mean(),
             selected[column][51:100].mean(),
             selected[column][101:150].mean(),
             selected[column][151:200].mean()
            ]
    return np.around(means, 1);


#Executes get_meantop200 function for all years and puts them into a 2D-list
#And then loops through the 2D-array and divides all the values into the group of 4 inside.
def divide_means():
    means = []
    for year in range(2011, 2017):
        means.append(get_meantop200(year, 'international_students') )
    
    means_grouped = []
    for i in range(0, 4):
        group_sum = 0
        for j in range(0, 4):
            group_sum += means[i][j]
        means_grouped.append(group_sum / 4)
    return means_grouped

#Creates the first visualization which is a bar chart that shows 4 bars with the divided
#universities of the top 200 with the average % international students for all years in the dataset.
def groupdivided_barchart():
    mean_grouped = divide_means()
    data = [go.Bar(
            # The index indicates the value of the group inside the list.
            x= ['Rang 1-50', 'Rang 51-100', 'Rang 101-150', 'Rang 151-200'],
            y= [mean_grouped[0], mean_grouped[1], mean_grouped[2], mean_grouped[3]],
            marker=dict(
                color='rgb(0,0,255)',
                line=dict(
                color='rgb(8,48,107)',
                width=3.5),
            ),
            text = np.around([mean_grouped[0], mean_grouped[1], mean_grouped[2], mean_grouped[3]], 2),
            textposition = 'auto',
    )]

    layout = go.Layout(
    title = 'Gemiddelde percentage internationale studenten op de top 200 universiteiten, per groep van 50, over 2011-2016',
    yaxis = go.layout.YAxis(
        tickmode = 'linear',
        ticksuffix = "%",
        ticklen= 6,
        tickwidth= 3,
        title = 'Percentage internationale studenten'
    ),
    xaxis = go.layout.XAxis(
        title = 'Groepen op ranglijst'
    ),
    )
    fig = go.Figure(data=data, layout=layout)
    iplot(fig, filename='basic-bar')

def get_meanitem(column):
    means = []
    for i in range(1, 201):
        filtered = converted_intstudent[(converted_intstudent['world_rank']) == i]
        means.append(filtered[column].mean())
    return np.around(means, 1)


int_students = get_meanitem('international_students') 
int_score = get_meanitem('international')

#Creates the second visualization of int_student. This graph will showcose with every boxplot the
#spread of the % international students of the universities divided into a group of 4 from the top 200 ranking
# The split happens at the beginning of every boxplot function.
def boxplot_intstudents():
    layout = go.Layout(
        title = 'De spreiding van het percentage internationale studenten binnen de top 200, verdeeld in groepen van 50',
        yaxis = go.layout.YAxis(
            ticksuffix = "%",
            ticklen= 6,
            tickwidth= 3,
            title = 'Percentage internationale studenten'
        ),
    )

    data = [
        go.Box(
            y=int_students[:50],
            #Showcases also every university of that group next to the boxplot on the left side.
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8,
            name = 'Rang 1-50'
        ),
        go.Box(
            y=int_students[51:100],
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8,
            name = 'Rang 51-100'
        ),
        go.Box(
            y=int_students[101:150],
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8,
            name = 'Rang 101-150'
        ),
        go.Box(
            y=int_students[151:200],
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8,
            name = 'Rang 151-200'
        )
    ]

    fig = go.Figure(data=data, layout=layout)
    iplot(fig, filename='boxplots')      
 

regr = linear_model.LinearRegression()
reshaped_score= int_score[:200].reshape(-1, 1)
reshaped_students= int_students[:200].reshape(-1,1)
regr.fit(reshaped_score,reshaped_students)


def scatter_intscore_intstudent():
    trace1 = go.Scatter(
        x = int_score[:50],
        y = int_students[:50],
        mode = 'markers',
        name = 'Rang 1-50'
    )
    trace2 = go.Scatter(
        x = int_score[51:100],
        y = int_students[51:100],
        mode = 'markers',
        name = 'Rang 51-100'
    )
    trace3 = go.Scatter(
        x = int_score[101:150],
        y = int_students[101:150],
        mode = 'markers',
        name = 'Rang 101-150'
    )
    trace4 = go.Scatter(
        x = int_score[151:200],
        y = int_students[151:200],
        mode = 'markers',
        name = 'Rang 151-200'
    )
    trace5 = go.Scatter(
        x= list(range(20,100)),
        y= list(0.47 * x for x in range(5,100)),
        mode="lines",
        line=dict(color="purple", width=3),
        name="Regressie"
    )

    layout = go.Layout(
        title = 'Verhouding tussen het percentage internationale studenten en DE internationale score bij de top 200 universiteiten',
        yaxis = go.layout.YAxis(
            tick0 = 5,
            dtick = 5,
            ticksuffix = "%",
            ticklen= 6,
            tickwidth= 3,
            range = [5,36],
            title = 'Percentage internationale studenten'
        ),
        xaxis = go.layout.XAxis(
            title = 'Internationale score',
            range = [30, 100]
        ),
    )

    data = [trace1, trace2, trace3, trace4, trace5]
    fig = go.Figure(data=data, layout=layout)
    iplot(fig, filename='basic-scatter')

# calculates the average mean and groups the dataframe by 1 or 2 attributes to choice.    
def groupby_mean(attribute1, attribute2 = 0, group = False, column = 0):
    if attribute2 != 0:
        country_stats = converted_intstudent.groupby([attribute1, attribute2]).mean()
        counts = converted_intstudent.groupby([attribute1, attribute2]).size()
    else:
        country_stats = converted_intstudent.groupby([attribute1]).mean()
        counts = converted_intstudent.groupby([attribute1]).size()
    country_stats['count'] = counts
    
    if group == True:
        country_stats = country_stats.sort_values(by=[column])

    return country_stats;

# Execute function with attributes needed for the percentage international score means.
grouped = groupby_mean('country', 0, group = True, column = 'international_students')

# Makes the barchart with the country and its average percentage international students.
def barchart_country_intstudents():
    data = [go.Bar( 
                x= grouped.index,
                y= grouped['international_students'],
                marker=dict(
                    color='rgb(40, 180, 25)',
                    line=dict(
                    color='rgb(8,48,107)',
                    width=3.5),
                ),
        )]

    layout = go.Layout(
        title = 'Gemiddelde percentage internationale studenten per land over de jaren 2011-2016',
        yaxis = go.layout.YAxis(
            tickmode = 'linear',
            ticksuffix = "%",
            tick0 = 0,
            dtick= 5,
            ticklen= 6,
            tickwidth= 3,
            automargin=True,
            title = 'Percentage internationale studenten',
            titlefont=dict(
            family='Arial, sans-serif',
            size=20,
            color='black'
            ),
        ),
        xaxis=dict(
            automargin=True,
            title = 'Land',
            titlefont=dict(
            family='Arial, sans-serif',
            size=20,
            color='black'
            ),
            showticklabels=True,
            tickangle=45,
            tickfont=dict(
            family='Old Standard TT, serif',
            size=14,
            color='black')
        )

    )
    fig = go.Figure(data=data, layout=layout)
    iplot(fig, filename='basic-bar')


country_stats_intstudent = groupby_mean('year', 'country', group = False)

# Creates the choropleth of the int_student
def choro_intstudent(raw, year, statistic, unit, zmax, rv):
    return go.Choropleth(
        zmin = 20,
        zmax = zmax,
        reversescale = rv,
        colorscale = [[0, 'rgb(50,50,255)'], [1, 'rgb(255,50,50)']],
        autocolorscale = False,
        locations = raw.index,
        z = raw[statistic].astype(float),
        locationmode = 'country names',
        marker = go.choropleth.Marker(
            line = go.choropleth.marker.Line(
                color = 'rgb(0,0,0)',
                width = .25
            )),
        colorbar = go.choropleth.ColorBar(
            title = unit),
        customdata = [year]
    )

#Crates the function to run the choropleth for intstudent
def worldmap_intstudent(statistic, title, unit, zmax, rv):
    data = [choro_intstudent(country_stats_intstudent.loc[year], year, statistic, unit, zmax, rv) for year in country_stats_intstudent.index.levels[0]]

    steps = []
    for i, d in enumerate(data):
        step = dict(method='restyle',
                    args=['visible', [False] * (len(data))],
                    label='Jaar {}'.format(d.customdata[0]))
        step['args'][1][i] = True
        steps.append(step)

    sliders = [dict(active=0,
                    pad={"t": 1},
                    steps=steps)]  

    layout = go.Layout(
        title = go.layout.Title(
            text = title
        ),
        geo = go.layout.Geo(
            scope = 'world',
            projection = go.layout.geo.Projection(type = 'equirectangular'),
            showlakes = True,
            lakecolor = 'rgb(255, 255, 255)'),
        sliders = sliders
    )

    fig = go.Figure(data = data, layout = layout)
    iplot(fig)
    
# Filter the country_stats_intstudent by year and colom and optionally sorts it.   
def filter_yearly(year, column, sort = True):
    filtered = country_stats_intstudent.loc[year]
    if sort == True:
        filtered = filtered.sort_values(by=[column])
    return filtered

# The default scatter trace function and what values to give
def dotplot_scatter(x_values, y_values, name, visible):
    trace = {"x": x_values, 
          "y": y_values, 
          "marker": {"color": "blue", "size": 12}, 
          "mode": "markers", 
          "name": name, 
          "type": "scatter",
          "visible": visible
    }
    return trace;

# Creates all the scatters which are used for the dotplot graph
def make_all_scatters(startyear, endyear, activeyear):
    traces = []
    for year in range(startyear, (endyear + 1), 1):
        if year == activeyear:
            traces.append(dotplot_scatter(filter_yearly(year, 'total_score')['total_score'], 
                            filter_yearly(year, 'total_score').index,
                            name = str(year),
                            visible = True,
                           ))
        else:
            traces.append(dotplot_scatter(filter_yearly(year, 'total_score')['total_score'], 
                            filter_yearly(year, 'total_score').index,
                            name = str(year),
                            visible = False,
                           ))
    return traces;

# Dotplot visualization function
def dotplot_totalscore():
    data = make_all_scatters(2011, 2016, 2011)
    layout = go.Layout(
        autosize=False,
        width=800,
        height=800,
        title = 'Gemiddelde totale score voor elk land per jaar',
        yaxis = go.layout.YAxis(
            ticklen= 6,
            tickwidth= 3,
            automargin=True,
            title = 'Land',
            titlefont=dict(
            family='Arial, sans-serif',
            size=20,
            color='black'
            ),
        ),
        xaxis=dict(
            automargin=True,
            title = 'Totale score',
            titlefont=dict(
            family='Arial, sans-serif',
            size=20,
            color='black'
            ),
            showticklabels=True,
            tickfont=dict(
            family='Old Standard TT, serif',
            size=14,
            color='black'),
            range = [0,100],
        )
    )

    updatemenus=list([
        dict(
            buttons=list([
                dict(
                    args=['visible', [True, False, False, False, False, False]],
                    label='2011',
                    method='restyle'
                ),

                dict(
                    args=['visible', [False, True, False, False, False, False]],
                    label='2012',
                    method='restyle'
                ),

                dict(
                    args=['visible', [False, False, True, False, False, False]],
                    label='2013',
                    method='restyle'
                ),

                dict(
                    args=['visible', [False, False, False, True, False, False]],
                    label='2014',
                    method='restyle'
                ),

                dict(
                    args=['visible', [False, False, False, False, True, False]],
                    label='2015',
                    method='restyle'
                ),

                dict(
                    args=['visible', [False, False, False, False, False, True]],
                    label='2016',
                    method='restyle'
                ),
            ]),
            direction = 'left',
            pad = {'r': 10, 't': 10},
            showactive = True,
            type = 'buttons',
            x = 0.1,
            xanchor = 'left',
            y = 1.08,
            yanchor = 'top',
            bgcolor = '#E2D3D0',
            bordercolor = '#FFFFFF',
            font = dict(size=18)
        ),
    ])

    layout['updatemenus'] = updatemenus

    fig = dict(data=data, layout=layout)
    iplot(fig, filename='basic_dot-plot') 

def choro(raw, year, statistic, unit, zmax, cls):
    return go.Choropleth(
        zmin = 0,
        zmax = zmax,
        colorscale = cls,
        autocolorscale = False,
        locations = raw.index,
        z = raw[statistic].astype(float),
        locationmode = 'country names',
        marker = go.choropleth.Marker(
            line = go.choropleth.marker.Line(
                color = 'rgb(0,0,0)',
                width = .25
            )),
        colorbar = go.choropleth.ColorBar(
            title = unit),
        customdata = [year], 
        visible= False
    )

def worldmap(statistic, title, unit, zmax, cls):
    data = [choro(country_stats.loc[year], year, statistic, unit, zmax, cls) for year in country_stats.index.levels[0]]
    data[len(data)-1].visible = True

    steps = []
    for i, d in enumerate(data):
        step = dict(method='restyle',
                    args=['visible', [False] * (len(data))],
                    label='Year {}'.format(d.customdata[0]))
        step['args'][1][i] = True
        steps.append(step)
        
    sliders = [dict(active=(len(data)-1),
                    pad={"t": 1},
                    steps=steps)]  

    layout = go.Layout(
        title = go.layout.Title(
            text = title
        ),
        geo = go.layout.Geo(
            scope = 'world',
            projection = go.layout.geo.Projection(type = 'equirectangular'),
            showlakes = True,
            lakecolor = 'rgb(255, 255, 255)'),
        sliders = sliders
    )

    fig = go.Figure(data = data, layout = layout)
    iplot(fig)

Japan = times[times['country'] == 'Japan']
HONGKONG = times[times['country'] == 'Hong Kong']
South_Korea = times[times['country'] == 'South Korea']
China = times[times['country'] == 'China']
Singapore = times[times['country'] == 'Singapore']
Taiwan = times[times['country'] == 'Taiwan']
Thailand = times[times['country'] == 'Thailand']
USA = times[times['country'] == 'United States of America']
asias = pd.concat([Japan, HONGKONG, South_Korea, China, Singapore, Taiwan, Thailand], ignore_index=True)


rankasia = asias[['percentile', 'year']].groupby(['year']).mean()
rankUSA = USA[['percentile', 'year']].groupby(['year']).mean()

count_asia= asias['year'].value_counts()
count_USA= USA['year'].value_counts()
count_asia= count_asia.to_frame(name=None)
count_USA= count_USA.to_frame(name=None)
count_asia= count_asia.iloc[::-1]
count_USA= count_USA.iloc[::-1]

univ2011 = times.loc[times['year'] == 2011]['university_name']
rankasia_filtered = asias.loc[asias['university_name'].isin(univ2011)].groupby(['year']).mean()
rankUSA_filtered = USA.loc[USA['university_name'].isin(univ2011)].groupby(['year']).mean()


def barplot_ranks():
    trace1 = go.Bar(
        x=rankasia.index,
        y=rankasia['percentile'],
        name='Azië',
        marker={
            "color": '#FF6961'
        }
    )

    trace2 = go.Bar(
        x=rankUSA.index,
        y=rankUSA['percentile'],
        name='USA',
        marker={
            "color": '#1e90ff'
        }
    )
    data = [trace1, trace2]

    layout = go.Layout(
        
        barmode='group',
        
        title=go.layout.Title(
            text='Gemiddelde universiteitspercentages van Azië vergeleken met de V.S.',
            
        ),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text='Jaar'
            ),
            type='category'
        ),
        yaxis = go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text='Gemiddeld beter dan %'
            )
        )
    )

    fig = go.Figure(data=data, layout=layout)
    iplot(fig)


def pie_yy():

    fig = {
    "data": [
        {
        "values": [count_asia.at[2015, 'year'],count_USA.at[2015, 'year']],
        "labels": ['Asia', 'USA'],
        "domain": {"column": 0},
        "name": "2015",
        "hoverinfo":"label+value",
        "textinfo": "label+value",
        "hole": .4,
        "type": "pie",
        "marker": {
            "colors": ['#FF6961', '#1e90ff']
        }
        },
        {
        "values": [count_asia.at[2016, 'year'],count_USA.at[2016, 'year']],
        "labels": ['Asia', 'USA'],
        "domain": {"column": 1},
        "name": "2016",
        "hoverinfo":"label+value",
        "textinfo": "label+value",
        "hole": .4,
        "type": "pie"
        }],
    "layout": {
            "title":"Aantal universiteiten op wereldranglijst in 2015-2016 Asia-USA",
            "grid": {"rows": 1, "columns": 2},
            "annotations": [
                {
                    "font": {
                        "size": 20
                    },
                    "showarrow": False,
                    "text": "2015",
                    "x": 0.20,
                    "y": 0.5
                },
                {
                    "font": {
                        "size": 20
                    },
                    "showarrow": False,
                    "text": "2016",
                    "x": 0.8,
                    "y": 0.5
                }
            ]
        }
    }

    iplot(fig)

def scatter_2011():
        
    trace1 = go.Scatter(
        x=rankasia_filtered.index,
        y=rankasia_filtered['percentile'],
    #     fill='tonexty',
        mode='lines+markers',
        line={
            "width": 5,
            "color": '#FF6961'
        },
        name='Azië',
    #     hoverinfo='none'
    )

    trace2 = go.Scatter(
        x=rankUSA_filtered.index,
        y=rankUSA_filtered['percentile'],
        fill='tonexty',
        fillcolor='rgba(135, 206, 250, 0.4)',
    #     opacity=0.1,
        mode='lines+markers',
        line={
            "width": 5,
            "color": '#1e90ff'
        },
        name='USA',
    #     hoverinfo="text",
    #     text=list('+' + str(int(u) - int(a)) for u, a in zip(rankUSA_filtered['percentile'], rankasia_filtered['percentile'])),
        textposition='top center'
    )
    lable = go.Scatter(
        x=rankUSA_filtered.index,
        y=rankUSA_filtered['percentile'].map(lambda x: x+2),
        mode='text',
        name='Verschil (%-punt)',
        hoverinfo="text",
        text=list('+' + str(int(u) - int(a)) for u, a in zip(rankUSA_filtered['percentile'], rankasia_filtered['percentile'])),
        textposition='top center'
    )
    data = [trace1, trace2, lable]

    layout = go.Layout(
        
        barmode='group',
        
        title=go.layout.Title(
            text='Gemiddelde universiteitspercentages van universiteiten die in 2011 al op de database zaten.',
            
        ),
        xaxis=go.layout.XAxis(
    #         gridwidth=5,
    #         range=[2012,2017],
    #         gridcolor='black',
            title=go.layout.xaxis.Title(
                text='Jaar'
            ),
            type='category' # het type van de X as is categorisch
        ),
        yaxis = go.layout.YAxis(
    #         gridwidth=5,
    #         gridcolor='black',
            title=go.layout.yaxis.Title(
                text='Gemiddeld beter dan %'
            ),
    #         range=[2014, 2017]
        )
    )

    fig = go.Figure(data=data, layout=layout)
    iplot(fig)
    

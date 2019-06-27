
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go
import math

# Start notebook mode
init_notebook_mode(connected=True)

import pandas as pd # we gebruiken pandas om de CSV data te laden en te visualiseren


times = pd.read_csv("timesData.csv")

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
    data = [choro(country_stats.loc[year], year, statistic, unit, zmax, cls) for year in 
    country_stats.index.levels[0]]
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
            text='Vergeljking tussen Amerikaanse en Aziatische universiteiten over de jaren',
            
        ),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text='Jaar'
            ),
            type='category'
        ),
        yaxis = go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text='Gemiddelde world ranking'
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
            text='Alleen universiteiten die in 2011 al op de database zaten',
            
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
                text='Gemiddelde precentile'
            ),
    #         range=[2014, 2017]
        )
    )

    fig = go.Figure(data=data, layout=layout)
    iplot(fig)

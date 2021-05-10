from unccalumni.web.dash.Basic import Basic
from unccalumni.plotting_constants import THEME, ColorPalette
from unccalumni.utils import DataFrameService

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from plotnine import *

import logging
import pandas as pd
import numpy as np
import random
import json
import geopandas
import pdb


logging.basicConfig(level = logging.INFO)

class Summary(Basic):

    class HTML_IDS:
        SCORE_DROPDOWN = "score_dropdown"
        EXCLUDE_US_INDIA = "exclude_us_india"

    def __init__(self,route,flaskApp):
        super().__init__(route,flaskApp , "Summary" )

    def filteredDf(self,checklist , year_checklist , program_checklist , exclude_us_india):
        df,geodf =  super().filteredDf(checklist , year_checklist , program_checklist )
        print(exclude_us_india , 1 in exclude_us_india)
        if 1 in exclude_us_india:
            df = df[~(df["PERM_ADDRESS_COUNTRY"].isin(["united states" , "india"]))]
        return df , geodf

    def per_regional(self, df , col , type , country_col , colors, n ):
      tempdf = df[[col , country_col]].value_counts().reset_index(name="counts")
      tempdf = tempdf.head(n)
      tempdf[col] = pd.Categorical(tempdf[col] , categories=tempdf[col], ordered=True)
      p = (
          ggplot(tempdf, aes(x=col , y="counts" , fill=country_col))
          + geom_col()
          + coord_flip()
          + theme_bw()
          + ggtitle(f"Top 20 Sources of Applicants by : {type}")
          + xlab(type)
          + ylab("Counts")
          + scale_fill_manual(values= colors, name="Country")
          + theme(figure_size=(3,3) ,legend_position=(.5, -.15) , legend_direction='horizontal')
      )
      return p

    def chart(self,dfs,checklist,year_checklist , program_checklist,exclude_us_india):
        if dfs is None:
            return self.getErrorPlot(self.ERROR_MSG)

        df , geo_df = dfs

        city_col = "PERM_ADDRESS_LINE_3"
        state_col = "PERM_ADDRESS_LINE_4"
        country_col = "PERM_ADDRESS_COUNTRY"
        n = 11
        selected_countries = df[country_col].value_counts().head(n).index
        colors= ColorPalette.mapRandomColors(selected_countries)

        df = df[df[country_col].isin(selected_countries)]

        p = (
            ggplot(df.groupby(["year" ,"program", "SEMESTER"]).size().reset_index(name="counts")
            ,aes(x="year" , y="counts" , group="SEMESTER" ,fill="SEMESTER"))
            + geom_col(position="dodge")
            + theme_bw()
            + facet_wrap("~ program")
            + theme(figure_size=(12,2))
            + ggtitle("Year Wise Applicant Counts")
            + scale_fill_manual(values=ColorPalette.mapRandomColors(df["SEMESTER"]))
        )
        return [p,
                self.per_regional(df , city_col , "Cities" , country_col , colors ,n),
                self.per_regional(df , state_col , "Region" , country_col, colors ,n)]

    def setupCallBacks(self):
        @self.app.callback(
            Output(component_id=Basic.HTML_IDS.IMG, component_property='children'),
            [Input(component_id=Basic.HTML_IDS.CHECKLIST, component_property='value')
            ,Input(component_id=Basic.HTML_IDS.YEAR_CHECKLIST, component_property='value')
            ,Input(component_id=Basic.HTML_IDS.PROGRAM_CHECKLIST, component_property='value')
            ,Input(component_id=Summary.HTML_IDS.EXCLUDE_US_INDIA, component_property='value')]
        )
        def filter_based_on_checklist_callback(checklist , year_checklist ,program_checklist , exclude_us_india):
            return self.filter_based_on_checklist(checklist = checklist
                                                    , year_checklist =year_checklist
                                                    ,program_checklist=program_checklist
                                                    , exclude_us_india=exclude_us_india)

    def makeInputLayout(self):
        return html.Div(className="row-fluid" , children=[
            super().makeInputLayout(),
            html.Div(className="row-fluid" , children=[
                dbc.Checklist(
                    options=[
                        {"label": "Exclude U.S and India", "value": 1},
                    ],
                    value=[0],
                    className="form-control",
                    inline=True,
                    id=Summary.HTML_IDS.EXCLUDE_US_INDIA,
                ),
            ])
        ])

    def makePlotImgsLayout(self, imgs):
        return html.Div(className="dash-container container p-0 m-0", children=[
             html.Div(className="row" ,children=[
                html.Div(className="col-md-12" , children = [
                    html.Div(className="row" ,children=[imgs[0]]),
                    html.Div(className="row" , children=[
                        html.Div(className="col-md-6" , children = [imgs[1]]),
                        html.Div(className="col-md-6" , children = [imgs[2]]),
                    ])
                ])])
             ])
             # ,
             # html.Div(className="row" ,children=[
             #    html.Div(className="col-md-12" , children = [imgs[1]])
             # ])

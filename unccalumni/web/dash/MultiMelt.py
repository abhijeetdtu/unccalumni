from unccalumni.web.dash.Basic import Basic
from unccalumni.plotting_constants import THEME ,ColorPalette
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

class MultiMelt(Basic):

    class HTML_IDS:
        SEGMENT = "segment"

    def __init__(self,route,flaskApp):
        super().__init__(route,flaskApp , "Applicant Background")

    def filteredDf(self,checklist , year_checklist , program_checklist , segment):
        return super().filteredDf(checklist , year_checklist , program_checklist )

    def col_multi_melt(self,df, str , type):
      edu_name_col = [c for c in df.columns if c.find(str) > -1]
      tempdf = df[edu_name_col].apply(lambda row: pd.Series(row.str.lower().unique()).value_counts(), axis=1).fillna(0)
      #tempdf.join(df)
      tempdf = tempdf.melt().groupby("variable").sum().reset_index()
      tempdf = tempdf.drop(0).sort_values("value" , ascending=False).head(30)
      n = tempdf.shape[0]
      tempdf["variable"] = pd.Categorical(tempdf["variable"] , ordered=True,categories=tempdf["variable"])
      p = (
          ggplot(tempdf, aes(x="variable" , y="value"))
          + geom_col()
          + coord_flip()
          + theme_bw()
          + ggtitle(f"Top {n} Sources of Applicants : {type}")
          + xlab(f"{type} Name")
          + ylab("Counts")
          + theme(figure_size = (8,5))
      )
      return p

    def chart(self,dfs,checklist,year_checklist , program_checklist , segment):
        if dfs is None:
            return self.getErrorPlot(self.ERROR_MSG)

        df , geo_df = dfs
        segment , label = segment.split("/")
        return [self.col_multi_melt(df, segment , label)]

    def setupCallBacks(self):
        @self.app.callback(
            Output(component_id=Basic.HTML_IDS.IMG, component_property='children'),
            [Input(component_id=Basic.HTML_IDS.CHECKLIST, component_property='value')
            ,Input(component_id=Basic.HTML_IDS.YEAR_CHECKLIST, component_property='value')
            ,Input(component_id=Basic.HTML_IDS.PROGRAM_CHECKLIST, component_property='value')
            ,Input(component_id=MultiMelt.HTML_IDS.SEGMENT, component_property='value')]
        )
        def filter_based_on_checklist_callback(checklist , year_checklist ,program_checklist , segment):
            return self.filter_based_on_checklist(checklist = checklist
                                                    , year_checklist =year_checklist
                                                    ,program_checklist=program_checklist
                                                    , segment=segment)

    def makeInputLayout(self):
        parentInputs = super().makeInputLayout()
        return html.Div(className="row", children=[
        html.Div(className="col-md-12" ,children=[
        html.Div(className="fluid-row", children=[
            dbc.FormGroup([
                    dbc.RadioItems(
                        id=MultiMelt.HTML_IDS.SEGMENT,
                        options=[
                            {'label': 'School', 'value': 'EDU_NAME/School'},
                            {'label': 'Degree', 'value': 'EDU_DEGREE/Degree'},
                            {'label': 'Degree Major', 'value': 'EDU_MAJOR/Major'}
                        ],
                        value='EDU_DEGREE/Degree',
                        inline=True
                    ),
                ])
        ]),
        parentInputs
        ])
        ])

    def makePlotImgsLayout(self, imgs):
        return html.Div(className="dash-container container p-0 m-0", children=[
             html.Div(className="row" ,children=[
                html.Div(className="col-md-12" , children = [imgs[0]])
             ])
             # ,
             # html.Div(className="row" ,children=[
             #    html.Div(className="col-md-12" , children = [imgs[1]])
             # ])

        ])

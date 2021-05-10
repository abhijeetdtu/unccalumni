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

class Scores(Basic):
    """
    Creates the Test Scores Dashboard.
    It inherits the `Basic` class and overrides `_filteredDf` and `_chart` methods
    """
    class HTML_IDS:
        SCORE_DROPDOWN = "score_dropdown"

    def __init__(self,route,flaskApp):
        self.score_columns = DataFrameService().get_score_columns()
        super().__init__(route,flaskApp , "Scores")

    def filteredDf(self,checklist , year_checklist , program_checklist , scores_column):
        return super().filteredDf(checklist , year_checklist , program_checklist )

    def chart(self,dfs,checklist,year_checklist , program_checklist,scores_column):
        print(scores_column)
        if dfs is None:
            return self.getErrorPlot(self.ERROR_MSG)

        df , geo_df = dfs

        score_df = df
        p = (
            ggplot(score_df[~score_df[scores_column].isna()] , aes(x=scores_column, fill="APP_FINAL_DECISION") )
            + geom_density(alpha=0.5)
            + geom_vline(score_df.groupby(["APP_FINAL_DECISION"])[scores_column].mean().reset_index(name="mean_score")
            , aes(xintercept = "mean_score" ,color="APP_FINAL_DECISION"))
            + scale_x_continuous(limits=(score_df[scores_column].quantile(0.01),score_df[scores_column].quantile(.95)))
            + scale_fill_manual(values= ColorPalette.mapRandomColors(score_df["APP_FINAL_DECISION"]))
            + scale_color_manual(values= ColorPalette.mapRandomColors(score_df["APP_FINAL_DECISION"]))
            + theme_bw()
            + theme(figure_size=(15,5) , panel_border=element_blank())
            + ggtitle(scores_column)
            + ylab(" ")
            + annotate("text" , x=168 , y= 0.1 , label="Mean Lines")
        )
        return [p]

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

    def setupCallBacks(self):
        @self.app.callback(
            Output(component_id=Basic.HTML_IDS.IMG, component_property='children'),
            [Input(component_id=Basic.HTML_IDS.CHECKLIST, component_property='value')
            ,Input(component_id=Basic.HTML_IDS.YEAR_CHECKLIST, component_property='value')
            ,Input(component_id=Basic.HTML_IDS.PROGRAM_CHECKLIST, component_property='value')
            ,Input(component_id=Scores.HTML_IDS.SCORE_DROPDOWN, component_property='value')]
        )
        def filter_based_on_checklist_callback(checklist , year_checklist ,program_checklist , scores_column):
            return self.filter_based_on_checklist(checklist = checklist
                                                    , year_checklist =year_checklist
                                                    ,program_checklist=program_checklist
                                                    , scores_column=scores_column)

    def makeInputLayout(self):
        parentInputs = super().makeInputLayout()
        return html.Div(className="row", children=[
        html.Div(className="col-md-12" ,children=[
        html.Div(className="fluid-row", children=[
            dcc.Dropdown(id=Scores.HTML_IDS.SCORE_DROPDOWN ,
            options=[{"label" : v , "value" : v} for v in self.score_columns],
            value=self.score_columns[0])
        ]),
        parentInputs
        ])
        ])

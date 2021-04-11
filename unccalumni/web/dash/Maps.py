from unccalumni.web.dash.Basic import Basic
from unccalumni.plotting_constants import THEME
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

class Maps(Basic):

    class HTML_IDS:
        IMG = "img"
        COUNTRY_SELECTION = "country_selection"
        YEAR_CHECKLIST = "year_checklist"
        PROGRAM_CHECKLIST = "program_checklist"

    def __init__(self,route,flaskApp , title=None):
        self.ERROR_MSG = "No Data Available"
        super().__init__(route,flaskApp , "Number of Applicants by Geography")


    def _filteredDf(self ,country_selection, year_checklist , program_checklist):
        alum_df= DataFrameService().get_alumni_df()

        if "All" not in year_checklist:
            alum_df = alum_df[alum_df["year"].isin(year_checklist)]
        if "All" not in program_checklist:
            alum_df = alum_df[alum_df["program"].isin(program_checklist)]

        # COUNTRIES
        if alum_df[alum_df["PERM_ADDRESS_COUNTRY"] == country_selection].shape[0] > 0:
            alum_df = alum_df[alum_df["PERM_ADDRESS_COUNTRY"] == country_selection]
            col = "PERM_ADDRESS_LINE_4"
        else:
            # ZIPCODES
            alum_df = alum_df[alum_df["PERM_ADDRESS_LINE_4"] == country_selection]
            col = "PERM_ADDRESS_LINE_5"

        #alum_df = alum_df[(alum_df["PERM_ADDRESS_COUNTRY"] == country_selection) | (alum_df["PERM_ADDRESS_LINE_4"] == country_selection) ]
        alum_df[col] = alum_df[col].str.lower()
        alum_df["NAME_1"] = alum_df[col]
        return alum_df , DataFrameService().get_india_geo_df() , DataFrameService().get_china_geo_df() ,DataFrameService().get_us_geo_df() ,DataFrameService().get_nc_geo_df()

    def plot_state(self,df , state_geo , name):
          india_state_app_counts = df.groupby(["NAME_1" ]).size()
          india_state_app_counts = india_state_app_counts.reset_index(name="counts")
          india_state_app_counts = india_state_app_counts[india_state_app_counts["counts"] > 1]
          merged = state_geo.merge(india_state_app_counts ,on="NAME_1" , how="left")

          if india_state_app_counts.shape[0] == 0:
              return self.getErrorPlot(self.ERROR_MSG)

          col =  "PERM_ADDRESS_LINE_3" if name == "NC" else "NAME_1"
          counts_df = df[col].value_counts().head(10).reset_index(name="counts")
          counts_df["index"] = pd.Categorical(counts_df["index"] , categories=counts_df["index"] , ordered=True)

          pbar = (
            ggplot(counts_df
                , aes(x="index" , y="counts"))
                + geom_col()
                + coord_flip()
                + xlab("Region")
                + ylab("Count of Applicants")
                + THEME.mt
                + theme(figure_size=(3,4))
          )
          pmap = (
              ggplot()
              + geom_map(merged , aes(fill="counts") , color=None)
              + THEME.mt
              + THEME.gradient_colors
              + theme(figure_size=(6,4))
          )
          return [pmap , pbar]

    def _chart(self,dfs,country_selection,year_checklist , program_checklist):
        if dfs is None:
            return self.getErrorPlot(self.ERROR_MSG)

        alum_df , india_geo , china_geo , us_geo , nc_geo = dfs

        country = {
            "india" : india_geo,
            "china" : china_geo,
            "united states": us_geo,
            "NC" : nc_geo
        }
        return self.plot_state(alum_df,country[country_selection],country_selection)

    def _filter_based_on_checklist(self,**kwargs):
        p = self.plot(**kwargs)

        logging.info("Plot to Img Src")
        src = self.plotToImgSrc(p)
        logging.info("Src to Dash Imgs")
        imgs  =self.srcToImgs(src)
        logging.info("Dash Imgs to Layout")
        children = self.makePlotImgsLayout(imgs)
        return children

    def makePlotImgsLayout(self, imgs):
        return html.Div(className="dash-container container p-0 m-0", children=[
             html.Div(className="row" ,children=[
                html.Div(className="col-md-8" , children = [imgs[0]]),
                html.Div(className="col-md-4" , children = [imgs[1]])
             ])
             # ,
             # html.Div(className="row" ,children=[
             #    html.Div(className="col-md-12" , children = [imgs[1]])
             # ])

        ])

    def setupCallBacks(self):
        @self.app.callback(
            Output(component_id=Basic.HTML_IDS.IMG, component_property='children'),
            [Input(component_id=Maps.HTML_IDS.COUNTRY_SELECTION, component_property='value')
            ,Input(component_id=Basic.HTML_IDS.YEAR_CHECKLIST, component_property='value')
            ,Input(component_id=Basic.HTML_IDS.PROGRAM_CHECKLIST, component_property='value')]
        )
        def filter_based_on_checklist(country_selection,year_checklist ,program_checklist):
            return self._filter_based_on_checklist(country_selection = country_selection,year_checklist =year_checklist ,program_checklist=program_checklist)

    def makeInputLayout(self):
        return html.Div(className="row" , children=[
                html.Div(className="col-md-12" , children=[
                    html.Div(className="row" , children=[
                        html.Div(className="col-md-12" , children=[
                            dbc.FormGroup([
                                    dbc.RadioItems(
                                        id=Maps.HTML_IDS.COUNTRY_SELECTION,
                                        options=[
                                            {'label': 'India', 'value': 'india'},
                                            {'label': 'China', 'value': 'china'},
                                            {'label': 'US', 'value': 'united states'},
                                            {'label': 'North Carolina', 'value': 'NC'}
                                        ],
                                        value='india',
                                        inline=True
                                    ),
                                ])

                        ])]),
                    html.Div(className="row" , children=[
                        html.Div(className="col-md-12" , children=[
                            dbc.Checklist(id=Basic.HTML_IDS.PROGRAM_CHECKLIST
                                        ,options=[{"label" : "All" , "value":"All"}] + [{"label" : v , "value" : v} for v in DataFrameService().get_unique_values("program")]
                                        , value=["All"]
                                        , className="form-control"
                                        ,inline=True),

                        ])]),
                    html.Div(className="row" , children=[
                        html.Div(className="col-md-12" , children=[
                            dbc.Checklist(id=Basic.HTML_IDS.YEAR_CHECKLIST
                                        ,options=[{"label" : "All" , "value":"All"}] + [{"label" : v , "value" : v} for v in DataFrameService().get_unique_values("year")]
                                        , value=["All"]
                                        , className="form-control"
                                        ,inline=True),

                        ])])
                        ])
        ])

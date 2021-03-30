from unccalumni.web.dash.DashApp import DashApp
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



logging.basicConfig(level = logging.INFO)

class Basic(DashApp):

    class HTML_IDS:
        IMG = "img"
        CHECKLIST = "checklist"

    def __init__(self,route,flaskApp):
        self.default_word = "modi"
        self.INPUT_PLACEHOLDER = "Search for something like Election, Coronavirus , Delhi"
        self.ERROR_MSG = "Term not found, try something else"
        self.NO_SELECTION_MSG = "Please select at least one option."

        self.TOP_N = 10
        super().__init__(route,flaskApp)


    def _filteredDf(self,checklist):
        alum_df= DataFrameService().get_alumni_df()
        if checklist[0] != "All":
            alum_df = alum_df[alum_df["PERM_ADDRESS_COUNTRY"].isin(checklist)]

        print(checklist)
        return alum_df , DataFrameService().get_geo_df()

    def _chart(self,dfs,checklist):
        if dfs is None:
            return self.getErrorPlot(self.ERROR_MSG)

        alum_df , geo_df = dfs
        counts_by_countries = pd.merge( geo_df ,
                               alum_df.groupby(["PERM_ADDRESS_COUNTRY"]).size().reset_index(name="counts") ,
                               right_on="PERM_ADDRESS_COUNTRY" ,left_on="name" , how="left" )

        #counts_by_countries["counts"] = counts_by_countries["counts"].fillna(0)
        print(counts_by_countries.head())
        #+ colors \
        p_counts = (
            ggplot(alum_df.groupby(["year" , "semester"]).size().reset_index(name="counts")
            ,aes(x="year" , y="counts" , group="semester" ,fill="semester"))
            + geom_col(position="dodge")
            + coord_flip()
            + theme_bw()
            + theme(figure_size=(8,3))
            + ggtitle("Year Wise Applicant Counts")
        )
        #counts_by_countries[~counts_by_countries["name"].isin(["india" , "united states"])]
        p_geo = (
            ggplot(counts_by_countries
            , aes( fill="counts"))
            + geom_map(na_rm=False)
            # + geom_col()
            # + geom_text(counts_by_countries[counts_by_countries["PERM_ADDRESS_COUNTRY"].isin(["india" , "united states"])],
            #                                 aes(label="PERM_ADDRESS_COUNTRY"))
            # + facet_wrap("~ semester + year")
            + theme_bw()
            + theme(figure_size=(12,5) , panel_grid_major_x=element_blank() , axis_text_x=element_blank())
            #+ scale_fill_continuous(breaks=np.geomspace(1,800 , 10))
            + ggtitle("Applicant Count by Countries")
            + xlab("")

        )
        return [p_counts , p_geo]


    def plot(self,checklist):
        df = self._filteredDf(checklist)
        p = self._chart(df,checklist)
        return p


    def setupOptions(self):
        #self.plot(None , None)
        pass

    def _filter_based_on_checklist(self,checklist):
        print(checklist)
        if len(checklist) == 0:
            # Nothing selected then show error image
            p = self.getErrorPlot(self.NO_SELECTION_MSG)
        else:
            p = self.plot(checklist)

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
                html.Div(className="col-md-5" , children = [imgs[0]]),
                html.Div(className="col-md-7" , children = [imgs[1]]),
             ])

        ])

    def setupCallBacks(self):
        @self.app.callback(
            Output(component_id=Basic.HTML_IDS.IMG, component_property='children'),
            [Input(component_id=Basic.HTML_IDS.CHECKLIST, component_property='value')]
        )
        def filter_based_on_checklist(checklist):
            return self._filter_based_on_checklist(checklist)

    def makeInputLayout(self):
        return html.Div(className="row" , children=[
            html.Div(className="col-md-12" , children=[
                dbc.Checklist(id=Basic.HTML_IDS.CHECKLIST
                            ,options=[{"label" : "All" , "value":"All"}] + [{"label" : v , "value" : v} for v in DataFrameService().get_top_countries(self.TOP_N)]
                            , value=["All"]
                            , className="form-control"
                            ,inline=True),

            ])
        ])

    def makeLayout(self):

        self.app.layout = html.Div(className="dash-container container p-0 m-0", children=[
            dcc.Loading(
                id="loading-holder",
                color=THEME.LOADER_COLOR,
                type=THEME.LOADER_TYPE,
                children=[
                    html.Div(className="row-fluid" , children=[
                        html.Div(id="title" ,children=[
                            html.Center(children=[html.H5("Applicant Counts")])
                        ]),
                        html.Div(id=Basic.HTML_IDS.IMG,  className="plot-holder-div")
                    ])
                ]
            ),
            self.makeInputLayout()

        ])

        self.setupCallBacks()

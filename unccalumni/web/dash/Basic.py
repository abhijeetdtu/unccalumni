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
import pdb


logging.basicConfig(level = logging.INFO)

class Basic(DashApp):
    """Root class for inheritance. Handles three filters in current state.
    1. Country Filter - called `checklist`
    2. Year Filter - `year_checklist`
    3. Program Filter - filter on `DSBA` or `HIA`

    Function Call Sequence is as follows
    1. `makeLayout` - sets up the UI elements and calls `setupCallBacks`
    2. `setupCallBacks` - passes all input changes to `filter_based_on_checklist` method
    3. `filter_based_on_checklist` - this method class `plot` method and converts plots to images for display
    4. `plot` - this method calls the two most important methods `_filteredDf` and `_chart`
    5. `filteredDf` - this method is for fetching the data and filtering it
    6. `chart` - this is for making the chart based on fetched and filtered data

    - To add new filters start from `makeLayout` and modify all functions as needed
    - To only fetch new data - override `_filteredDf`
    - To just add another chart to existing data, only override `_chart` method
    """

    class HTML_IDS:
        IMG = "img"
        CHECKLIST = "checklist"
        YEAR_CHECKLIST = "year_checklist"
        PROGRAM_CHECKLIST = "program_checklist"

    def __init__(self,route,flaskApp , title=None):
        """Create a Basic App

        parameters:
        - route: the web route to which this app will be attached
        - flaskApp : the flask app object to which this app will be attached

        example:

            from flask import Flask
            app = Flask(__name__)

            basic_dash = Basic("/dash/basic" , app)
        """

        self.default_word = "modi"
        self.INPUT_PLACEHOLDER = "Search for something like Election, Coronavirus , Delhi"
        self.ERROR_MSG = "Term not found, try something else"
        self.NO_SELECTION_MSG = "Please select at least one option."
        self.TITLE= title or "Applicant Counts"
        self.TOP_N = 9
        super().__init__(route,flaskApp)


    def filteredDf(self,checklist , year_checklist , program_checklist):
        """This is main method for fetching data that should be overridden when inheriting. This is called from
        `setupCallbacks` method which sets up Dash Based UI elements and callbacks for filtering.

        You should load your dataframe here using `DataFrameService` and filter it based on the parameters passed.

        parameters:
        - checklist - this is the list of countries selected in the UI
        - year_checklist - this is the list of years selected in the UI
        - program_checklist - this is the list of programs (DSBA , HIA) selected in the UI
        """

        alum_df= DataFrameService().get_alumni_df()
        if "All" not in checklist:
            alum_df = alum_df[alum_df["PERM_ADDRESS_COUNTRY"].isin(checklist)]
        if "All" not in year_checklist:
            alum_df = alum_df[alum_df["year"].isin(year_checklist)]

        if "All" not in program_checklist:
            alum_df = alum_df[alum_df["program"].isin(program_checklist)]

        return alum_df , DataFrameService().get_geo_df()

    def chart(self,dfs,checklist,year_checklist , program_checklist):
        """This is main method for creating a plot that should be overridden when inheriting. This is called from
        `setupCallbacks` method which sets up Dash Based UI elements and callbacks for filtering.

        You should load your dataframe here using `DataFrameService` and filter it based on the parameters passed.

        parameters:
        - dfs : these are the dataframes returned from `_filteredDf` method
        - checklist - this is the list of countries selected in the UI
        - year_checklist - this is the list of years selected in the UI
        - program_checklist - this is the list of programs (DSBA , HIA) selected in the UI
        """
        if dfs is None:
            return self.getErrorPlot(self.ERROR_MSG)

        alum_df , geo_df = dfs
        counts_by_countries_by_all = pd.merge( geo_df ,
                               alum_df.groupby(["PERM_ADDRESS_COUNTRY"]).size().reset_index(name="counts") ,
                               right_on="PERM_ADDRESS_COUNTRY" ,left_on="name" , how="left" )

        year_diff = (
            pd.crosstab(alum_df[ "PERM_ADDRESS_COUNTRY"] , alum_df["year"] ,alum_df[ "PERSONID"] , aggfunc=lambda df : df.size)
                 .fillna(0)
                 .reset_index()
                 .melt(id_vars="PERM_ADDRESS_COUNTRY")
                 .groupby("PERM_ADDRESS_COUNTRY")
                 .apply(lambda df : pd.Series(df["value"].diff().values
                                              , index=df["year"].unique()))
                 .reset_index()
                 .melt(id_vars="PERM_ADDRESS_COUNTRY")
                 .fillna(0)
        )
        year_diff["variable"] = pd.Categorical(year_diff["variable"] , categories =year_diff["variable"].unique() ,ordered=True)
        year_diff["is_positive"] = year_diff["value"] > 0
        #counts_by_countries["counts"] = counts_by_countries["counts"].fillna(0)
        #+ colors \
        p_counts = (
            ggplot(alum_df.groupby(["year" , "SEMESTER"]).size().reset_index(name="counts")
            ,aes(x="year" , y="counts" , group="SEMESTER" ,fill="SEMESTER"))
            + geom_col(position="dodge")
            + coord_flip()
            + THEME.cat_colors
            + THEME.mt
            + theme(figure_size=(8,3), panel_grid_major=element_blank())
            + ggtitle("Year Wise Applicant Counts")
        )
        #counts_by_countries[~counts_by_countries["name"].isin(["india" , "united states"])]
        p_geo = (
            ggplot(counts_by_countries_by_all
            , aes( fill="counts"))
            + geom_map(na_rm=False)
            # + geom_col()
            # + geom_text(counts_by_countries[counts_by_countries["PERM_ADDRESS_COUNTRY"].isin(["india" , "united states"])],
            #                                 aes(label="PERM_ADDRESS_COUNTRY"))
            # + facet_wrap("~ SEMESTER + year")
            + THEME.gradient_colors
            + THEME.mt
            + theme(figure_size=(7,6)
                , panel_grid_major=element_blank()
                , axis_text=element_blank())
            #+ scale_fill_continuous(breaks=np.geomspace(1,800 , 10))
            + ggtitle("Total Applicant Count by Countries")
            + xlab("")

        )

        p_diff =(
        ggplot(year_diff , aes(x="variable" , y="value" , group="PERM_ADDRESS_COUNTRY"))
        + geom_line(color="#023047")
        + geom_hline(yintercept=0 , color="#4f5d75")
        + geom_text(data=year_diff[year_diff["variable"] ==  year_diff["variable"].max()]
                    , mapping=aes(label="PERM_ADDRESS_COUNTRY" ,color="is_positive")
                    , nudge_x=0.01
                    , ha="left"
                    ,alpha=0.8)
            + THEME.mt
            + theme(figure_size=(10,5)
                    , panel_grid_major_y=element_blank())
            #+ scale_y_continuous(values=np.arange(-10,10,5))
            + scale_color_manual(guide=False , values=THEME.colors_dark)
            #+ scale_fill_manual(values={True : "#2a9d8f" , False : "#f4a261"} , guide=False)
            + ylab("Difference from Previous Year")
            + xlab("Year")
            + ggtitle("Year over Year - Application Count Difference")


        )
        return [p_counts , p_geo  , p_diff]


    def plot(self,**kwargs):
        """
            This method passes along all the `**kwargs` arguments from `filter_based_on_checklist` method to `filteredDf` and `chart` methods
        """
        df = self.filteredDf(**kwargs)
        p = self.chart(df,**kwargs)
        return p


    def setupOptions(self):
        #self.plot(None , None)
        pass

    def filter_based_on_checklist(self,**kwargs):
        """
            This method passes along all the `**kwargs` arguments `plot` method and converts the returned plots to Images for display in the UI
        """
        p = self.plot(**kwargs)

        logging.info("Plot to Img Src")
        src = self.plotToImgSrc(p)
        logging.info("Src to Dash Imgs")
        imgs  =self.srcToImgs(src)
        logging.info("Dash Imgs to Layout")
        children = self.makePlotImgsLayout(imgs)
        return children

    def makePlotImgsLayout(self, imgs):
        """
            You should modify this method to change how the plots are laid out in the UI
            This uses `Bootstrap` system of rows and columns, which can be used to define the layout

            parameters:
            - imgs : list of images which have been generated for each plot returned by the `chart` method
        """
        return html.Div(className="dash-container container p-0 m-0", children=[
             html.Div(className="row" ,children=[
                html.Div(className="col-md-5" , children = [imgs[1]]),
                html.Div(className="col-md-7" , children = [imgs[2]]),
             ])
             # ,
             # html.Div(className="row" ,children=[
             #    html.Div(className="col-md-12" , children = [imgs[1]])
             # ])

        ])

    def setupCallBacks(self):
        """
            This method is sets up `Dash` callbacks, linking the inputs created in `makeInputLayout` to the `_filter_based_on_checklist` method
            If you do decide to add more filters , you should first override `makeInputLayout` and then this method.

            parameters:
            - checklist - this is the list of countries selected in the UI
            - year_checklist - this is the list of years selected in the UI
            - program_checklist - this is the list of programs (DSBA , HIA) selected in the UI
        """
        @self.app.callback(
            Output(component_id=Basic.HTML_IDS.IMG, component_property='children'),
            [Input(component_id=Basic.HTML_IDS.CHECKLIST, component_property='value')
            ,Input(component_id=Basic.HTML_IDS.YEAR_CHECKLIST, component_property='value')
            ,Input(component_id=Basic.HTML_IDS.PROGRAM_CHECKLIST, component_property='value')]
        )
        def filter_based_on_checklist_callback(checklist , year_checklist ,program_checklist):
            return self.filter_based_on_checklist(checklist = checklist , year_checklist =year_checklist ,program_checklist=program_checklist)

    def makeInputLayout(self):
        """
            This method creates the UI input elements one for each of the following
            - checklist - this is a HTML checklist list of countries selected in the UI
            - year_checklist - this is a HTML checklist of years selected in the UI
            - program_checklist - this is a HTML checklist of programs (DSBA , HIA) selected in the UI

            These are dynamically populated using the `DataFrameService`
        """
        return html.Div(className="row" , children=[
                html.Div(className="col-md-12" , children=[
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

                        ])]),
                    html.Div(className="row" , children=[
                        html.Div(className="col-md-12" , children=[
                            dbc.Checklist(id=Basic.HTML_IDS.CHECKLIST
                                        ,options=[{"label" : "All" , "value":"All"}] + [{"label" : v , "value" : v} for v in DataFrameService().get_top_countries(self.TOP_N)]
                                        , value=["All"]
                                        , className="form-control"
                                        ,inline=True),

                        ])])
                    ])
        ])

    def makeLayout(self):
        """
            This method creates the overall layout of the dashboard.
            Dashboard has
            1. Title
            2. horizontal Separator : HR
            3. Placeholder for all the plots

            This method also calls `makeInputLayout` and `setupCallBacks`
            This method should rarely be updated. If you need to add filters or change plot arrangement
            make changes to `makeInputLayout` or `makePlotImgsLayout`
        """
        self.app.layout = html.Div(className="dash-container container p-0 m-0", children=[
            dcc.Loading(
                id="loading-holder",
                color=THEME.LOADER_COLOR,
                type=THEME.LOADER_TYPE,
                children=[
                    html.Div(className="row-fluid" , children=[
                        html.Div(id="title" ,children=[
                            html.Center(children=[html.H5(self.TITLE)])
                        ]),
                        html.Hr(className="hr"),
                        html.Div(id=Basic.HTML_IDS.IMG,  className="plot-holder-div")
                    ])
                ]
            ),
            self.makeInputLayout()

        ])

        self.setupCallBacks()

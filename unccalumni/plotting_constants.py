from plotnine import (theme
,element_blank
, element_rect
, element_text
, scale_fill_manual
, scale_color_manual
,scale_fill_gradient , theme_bw)

from numpy import random
from pandas import Series
import json

class THEME():
    bgcolor = "#293241"
    LOADER_COLOR = "#2a9d8f"
    LOADER_TYPE = "dot"

    colors_light = ["#d88c9a","#f2d0a9" , "#f1e3d3" , "#99c1b9" , "#8e7dbe" , "#50514f" , "#f25f5c" ,"#ffe066" , "#247ba0" , "#70c1b3" , "#c97c5d" , "#b36a5e"]
    colors_dark = ["#e07a5f" , "#3d405b" ,"#81b29a" , "#2b2d42" , "#f77f00" , "#6d597a"]
    # mt = theme(panel_background=element_rect(fill=bgcolor)
    #            ,plot_background=element_rect(fill=bgcolor)
    #            , axis_text_x = element_text(color="black")
    #            , axis_text_y = element_text(color="black")
    #            , strip_margin_y=0.05
    #            , strip_margin_x=0.5)

    mt = theme_bw() + theme(panel_border = element_blank())


    cat_colors = scale_fill_manual(values = colors_light)
    cat_colors_lines = scale_color_manual(values = colors_light)
    gradient_colors = scale_fill_gradient( "#ce4257" , "#aad576")
    FILL = 1
    COLOR = 2

    LONG_FIGURE = (10,20)

class ColorPalette:

    alreadyMapped = {}

    @staticmethod
    def mapRandomColors(series):
        unq = series.unique()
        key = "-".join(unq)
        if key in ColorPalette.alreadyMapped:
            return ColorPalette.alreadyMapped[key]

        n = len(unq)

        if n > len(THEME.colors_light):
            raise Exception(f"{n} : Number of Categories is greater than {len(THEME.colors_light)}.")

        colors = random.choice(THEME.colors_light , n , replace=False)
        s = Series(colors , index=unq ,name="color")
        colorDict =  json.loads(s.to_json(orient="index"))
        ColorPalette.alreadyMapped[key] = colorDict
        return ColorPalette.alreadyMapped[key]

    # @staticmethod
    # def sticky_color_map(series):
    #     unq = series.unique()
    #     n = len(unq)
    #
    #     if n > len(THEME.colors_light):
    #         raise Exception(f"Number of Categories is greater than {len(THEME.colors_light)}.")
    #
    #
    #     colors_new = random.choice(THEME.colors_light , n - len(colors) , replace=False)
    #     for
    #     s = Series(colors + colors_new , index=unq ,name="color")
    #     colorDict =  json.loads(s.to_json(orient="index"))
    #     return ColorPalette.alreadyMapped[key]

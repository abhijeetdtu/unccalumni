import logging
import pathlib
import os
import pandas as pd
import geopandas
import re

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def getLogging():
    logging.basicConfig(level=logging.DEBUG)
    return logging


class DataFrameService(metaclass=Singleton):

    def __init__(self):
        self.path_to_files = os.path.join(pathlib.Path(__file__).resolve().parent.absolute() , "data")
        self.cache = {}

    def cached_access(self ,key, func , **kwargs):
        if key in self.cache:
            return self.cache[key]
        self.cache[key] = func(**kwargs)
        return self.cache[key]

    def _get_geo_df(self):
        world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
        world["name"] = world["name"].str.lower()
        mappings = {"south korea" : "korea, republic of" , "taiwan" : "taiwan, province of china" , "united states of america" : "united states"}
        for k,v in mappings.items():
            world["name"].loc[world["name"] == k ] = v
        return world

    def get_geo_df(self):
        return self.cached_access("geo_df" , self._get_geo_df)

    def _get_india_geo_df(self):
        india_geo = geopandas.read_file(os.path.join(self.path_to_files , "india_states" , "3e563fd0-8ea1-43eb-8db7-3cf3e23174512020330-1-layr7d.ivha.shp"))
        india_geo["NAME_1"] = india_geo["NAME_1"].str.lower()
        return india_geo

    def get_india_geo_df(self):
        return self.cached_access("india_geo_df" , self._get_india_geo_df)

    def _get_china_geo_df(self):
        china_geo = geopandas.read_file(os.path.join(self.path_to_files , "china_states" , "chn_admbnda_adm1_ocha_2020.shp"))
        china_geo = china_geo.rename({"ADM1_EN": "NAME_1"} , axis=1)
        china_geo["NAME_1"] = china_geo["NAME_1"].str.lower()
        china_geo["NAME_1"] = china_geo["NAME_1"].str.replace("province" , "").str.strip(" ")
        return china_geo

    def get_china_geo_df(self):
        return self.cached_access("china_geo_df" , self._get_china_geo_df)

    def _get_us_geo_df(self):
        geo = geopandas.read_file(os.path.join(self.path_to_files , "us_states" , "cb_2018_us_state_500k.shp"))
        geo = geo.rename({"STUSPS": "NAME_1"} , axis=1)
        geo["NAME_1"] = geo["NAME_1"].str.lower()
        #geo["geo_id"] = geo["AFFGEOID"].apply(lambda v : re.findall("\d+US(\d+)" , v)[0])
        #geo["geo_id"] = geo["geo_id"].astype("int")
        geo = geo[~geo["NAME_1"].isin(["hi" , "ak" , "vi" , "as" , "gu" , "mp" , "pr"])]
        #geo = geo[geo["geo_id"] < 50]
        #china_geo["NAME_1"] = china_geo["NAME_1"].str.replace("province" , "").str.strip(" ")
        return geo

    def get_us_geo_df(self):
        return self.cached_access("us_geo_df" , self._get_us_geo_df)

    def _get_nc_geo_df(self):
        geo = geopandas.read_file(os.path.join(self.path_to_files , "nc_zipcodes" , "ZIP_Code_Tabulation_Areas.shp"))
        geo = geo.rename({"GEOID10": "NAME_1"} , axis=1)
        return geo

    def get_nc_geo_df(self):
        return self.cached_access("nc_geo_df" , self._get_nc_geo_df)

    def _get_nc_county_geo_df(self):
        geo = geopandas.read_file(os.path.join(self.path_to_files , "nc_counties" , "counties.shp"))
        return geo

    def get_nc_county_geo_df(self):
        return self.cached_access("nc_geo_county_df" , self._get_nc_county_geo_df)

    def _get_alumni_df(self):
        alum_df =  pd.read_csv(os.path.join(self.path_to_files , "combined_3.csv"))
        alum_df["PERM_ADDRESS_COUNTRY"]= alum_df["PERM_ADDRESS_COUNTRY"].str.lower()
        return alum_df

    def get_alumni_df(self):
        return self.cached_access("alumni_df" , self._get_alumni_df)

    def _get_top_countries(self , n):
        df = self.cached_access("alumni_df" , self._get_alumni_df)
        return list(df["PERM_ADDRESS_COUNTRY"].value_counts().head(n).index.values)
        #return df[df["PERM_ADDRESS_COUNTRY"].isin(countries)]

    def get_top_countries(self,n):
        return self.cached_access("top_countries" , self._get_top_countries , n=n)

    def _get_score_columns(self):
        score_columns = ["GRE" , "TOEFL" , "IELTS" , "MAT" , "GMAT"]
        df = self.cached_access("alumni_df" , self._get_alumni_df)
        score_columns = [ c for c in df.columns for s in score_columns if (c.find(s) == 0) and (c.find("SCORE") > -1)]
        return score_columns
        #return df[df["PERM_ADDRESS_COUNTRY"].isin(countries)]

    def get_score_columns(self):
        return self.cached_access("score_columns" , self._get_score_columns)

    def _get_unique_values(self, column , n = -1):
        df = self.cached_access("alumni_df" , self._get_alumni_df)
        vals= list(df[column].value_counts().index.values)
        return vals if n == -1 else vals[:n]

    def get_unique_values(self, column,n=-1):
        return self.cached_access(f"unique_values_{column}" , self._get_unique_values,column=column, n=n)

import logging
import pathlib
import os
import pandas as pd
import geopandas

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def getLogging():
    logging.basicConfig(level=logging.INFO)
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

    def _get_alumni_df(self):
        dfs = []
        for f in os.listdir(self.path_to_files):
          if f.find('.xlsx') > -1:
            path = pathlib.Path(self.path_to_files , f)
            df = pd.read_excel(path ,skiprows=4)
            year = f.replace("DSBA Applicant Pool " , "").replace(".xlsx" ,"").strip(" ")
            sem , year = year.split(" ")
            df["year"] = year
            df["semester"] = sem
            dfs.append(df)
        alum_df =  pd.concat(dfs)
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

#importing the libraries 
import geopandas as gpd
import rasterio as rio
from rasterstats import zonal_stats
import matplotlib.pyplot as plt 
import glob 
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm

# def access_files(file_path):
#     file_list = glob.glob(file_path+'*.tif')
#     print(file_list)
# raster_dir = './Data/'
# access_files(raster_dir)

# re_ordering the list 
file_list = ['./Data\\ph.tif', 
            './Data\\nitrogen.tif', 
            './Data\\p2o5.tif', 
            './Data\\K250.tif',
            './Data\\organic.tif',
            './Data\\Zn250.tif',
            './Data\\boron.tif',
            './Data\\sand.tif',
            './Data\\slit.tif',
           './Data\\clay.tif' ]


nepal_dist = gpd.read_file('./Data/Nepal_Districts.shp')
columns_to_drop = ['STATE_CODE','GaPa_NaPa', 'Type_GN', 'Province']
nepal_dist = nepal_dist.drop(columns= columns_to_drop)

## create a function that classifies nepal districts into terai hills and subdomains
def classify_dist_domain (nepal_districts): 
    terai_dist = ['JHAPA','MORANG','SUNSARI', 'SAPTARI', 'SIRAHA','DHANUSHA','MAHOTTARI','SARLAHI',
                  'RAUTAHAT','BARA','PARSA','CHITAWAN','NAWALPARASI_E','NAWALPARASI_W', 'RUPANDEHI',
                  'KAPILBASTU','DANG', 'BANKE','BARDIYA','KAILALI', 'KANCHANPUR','DANG', 'SURKHET']
    terai_eastern = ['JHAPA','MORANG','SUNSARI']
    terai_central = ['SAPTARI', 'SIRAHA','DHANUSHA','MAHOTTARI','SARLAHI','RAUTAHAT','BARA','PARSA']
    terai_western = ['CHITAWAN','NAWALPARASI_E','NAWALPARASI_W', 'RUPANDEHI']
    terai_farwestern = ['BANKE','BARDIYA','KAILALI', 'KANCHANPUR']
    terai_inner = ['CHITAWAN','DANG', 'SURKHET']
    nepal_districts['Domain'] = ''
    nepal_districts['Sub_domain'] = ''
    for idx, row  in nepal_districts.iterrows(): 
        if row['DISTRICT'] in terai_dist: 
            nepal_districts.at[idx , 'Domain'] = 'Terai'
        else: 
            nepal_districts.at[idx, 'Domain'] = 'Hill'
        if row['DISTRICT'] in terai_eastern: 
            nepal_districts.at[idx , 'Sub_domain'] = 'Eastern_terai'
        elif row['DISTRICT'] in terai_central:
            nepal_districts.at[idx, 'Sub_domain'] = 'Central_terai'
        elif row['DISTRICT'] in terai_western: 
            nepal_districts.at[idx, 'Sub_domain'] = 'Western_terai'
        elif row['DISTRICT'] in terai_farwestern : 
            nepal_districts.at[idx , 'Sub_domain'] = 'Farwest_terai'
        elif row['DISTRICT'] in terai_inner: 
            nepal_districts.at[idx , 'Sub_domain'] = 'Inner_terai'
        else: 
            nepal_dist.at[idx , 'Sub_domain'] = 'Hill'
            
    return nepal_districts 
    
new_gdf = classify_dist_domain(nepal_dist)

def soil_property_calc (raster_list, geo_df): 
    column_names = ['pH','TN%','P2O5_kg/ha','K2O_kg/ha','OM%','Zinc(ppm)','Boron(ppm)','Sand%','Slit%','Clay%']
    for file, column_name in zip(raster_list, column_names):
        with rio.open(file) as src:
            geo_df.loc[:,column_name] = zonal_stats(geo_df, src.read(1) , affine = src.transform,nodata = src.nodata, stats = "mean")
            geo_df.loc[:,column_name] = new_gdf.apply(lambda row: round(row[column_name]['mean'],2), axis=1)
    return geo_df 

gdf_sp = soil_property_calc(file_list , new_gdf)



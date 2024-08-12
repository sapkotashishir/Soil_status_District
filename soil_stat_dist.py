#importing the libraries 
import pandas as pd 
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

def classify_domain_nutrients(selected_palika):
    for index, row in selected_palika.iterrows():
        domain = row['Domain']
        pH = row['pH']
        TN_percent = row['TN%']
        P2O5_kg_ha = row['P2O5_kg/ha']
        K2O_kg_ha = row['K2O_kg/ha']
        OM_percent = row['OM%']
        Zinc_ppm = row['Zinc(ppm)']
        Boron_ppm = row['Boron(ppm)']
        Sand_percent = row['Sand%']
        Slit_percent = row['Slit%']
        Clay_percent = row['Clay%']

        # Initialize new columns for ratings
        selected_palika.at[index, 'pH_rating'] = None
        selected_palika.at[index, 'OM_rating'] = None
        selected_palika.at[index, 'TN_rating'] = None
        selected_palika.at[index, 'P2O5_rating'] = None
        selected_palika.at[index, 'K2O_rating'] = None
        selected_palika.at[index, 'Boron_rating'] = None
        selected_palika.at[index, 'Zinc_rating'] = None

        # Classification of pH and its rating
        if 0.0 < pH <= 4.0:
            selected_palika.at[index, 'pH_rating'] = 'Very High acidic'
        elif 4.0 < pH <= 5.5:
            selected_palika.at[index, 'pH_rating'] = 'High Acidic'
        elif 5.5 < pH <= 6.0:
            selected_palika.at[index, 'pH_rating'] = 'Medium Acidic'
        elif 6.0 < pH <= 6.5:
            selected_palika.at[index, 'pH_rating'] = 'Low Acidic'
        elif 6.5 < pH <= 7.5:
            selected_palika.at[index, 'pH_rating'] = 'Neutral'
        elif 7.5 < pH <= 8.0:
            selected_palika.at[index, 'pH_rating'] = 'Low Alkaline'
        elif 8.0 < pH <= 8.5:
            selected_palika.at[index, 'pH_rating'] = 'Low Alkaline'
        elif 8.5 < pH <= 10.0:
            selected_palika.at[index, 'pH_rating'] = 'Very High Alkaline'

        # Classification of Organic Matter (OM %)
        if domain == 'Hill':
            if OM_percent < 0.75:
                selected_palika.at[index, 'OM_rating'] = 'Very low'
            elif 0.75 <= OM_percent < 1.5:
                selected_palika.at[index, 'OM_rating'] = 'Low'
            elif 1.5 <= OM_percent < 3.0:
                selected_palika.at[index, 'OM_rating'] = 'Medium'
            elif 3.0 <= OM_percent < 5.0:
                selected_palika.at[index, 'OM_rating'] = 'High'
            else:
                selected_palika.at[index, 'OM_rating'] = 'Very High'

            # Classification of Total Nitrogen (TN %)
            if TN_percent < 0.03:
                selected_palika.at[index, 'TN_rating'] = 'Very low'
            elif 0.03 <= TN_percent < 0.07:
                selected_palika.at[index, 'TN_rating'] = 'Low'
            elif 0.07 <= TN_percent < 0.15:
                selected_palika.at[index, 'TN_rating'] = 'Medium'
            elif 0.15 <= TN_percent < 0.25:
                selected_palika.at[index, 'TN_rating'] = 'High'
            else:
                selected_palika.at[index, 'TN_rating'] = 'Very High'

            # Classification of P2O5 kg/ha
            if P2O5_kg_ha < 11.2:
                selected_palika.at[index, 'P2O5_rating'] = 'Very low'
            elif 11.2 <= P2O5_kg_ha < 28:
                selected_palika.at[index, 'P2O5_rating'] = 'Low'
            elif 28 <= P2O5_kg_ha < 56:
                selected_palika.at[index, 'P2O5_rating'] = 'Medium'
            elif 56 <= P2O5_kg_ha < 112:
                selected_palika.at[index, 'P2O5_rating'] = 'High'
            else:
                selected_palika.at[index, 'P2O5_rating'] = 'Very High'

            # Classification of K2O kg/ha
            if K2O_kg_ha < 55:
                selected_palika.at[index, 'K2O_rating'] = 'Very low'
            elif 55 <= K2O_kg_ha < 110:
                selected_palika.at[index, 'K2O_rating'] = 'Low'
            elif 110 <= K2O_kg_ha < 280:
                selected_palika.at[index, 'K2O_rating'] = 'Medium'
            elif 280 <= K2O_kg_ha < 500:
                selected_palika.at[index, 'K2O_rating'] = 'High'
            else:
                selected_palika.at[index, 'K2O_rating'] = 'Very High'

            # Classification of Boron (ppm)
            if Boron_ppm < 0.4:
                selected_palika.at[index, 'Boron_rating'] = 'Very low'
            elif 0.4 <= Boron_ppm < 0.7:
                selected_palika.at[index, 'Boron_rating'] = 'Low'
            elif 0.7 <= Boron_ppm < 1.2:
                selected_palika.at[index, 'Boron_rating'] = 'Medium'
            elif 1.2 <= Boron_ppm < 2.0:
                selected_palika.at[index, 'Boron_rating'] = 'High'
            else:
                selected_palika.at[index, 'Boron_rating'] = 'Very High'

            # Classification of Zinc (ppm)
            if Zinc_ppm < 0.5:
                selected_palika.at[index, 'Zinc_rating'] = 'Very low'
            elif 0.5 <= Zinc_ppm < 1.0:
                selected_palika.at[index, 'Zinc_rating'] = 'Low'
            elif 1.0 <= Zinc_ppm < 3.0:
                selected_palika.at[index, 'Zinc_rating'] = 'Medium'
            elif 3.0 <= Zinc_ppm < 6.0:
                selected_palika.at[index, 'Zinc_rating'] = 'High'
            else:
                selected_palika.at[index, 'Zinc_rating'] = 'Very High'

        elif domain == 'Terai':
            # Classification of Organic Matter (OM %)
            if OM_percent < 1.0:
                selected_palika.at[index, 'OM_rating'] = 'Very low'
            elif 1.0 <= OM_percent < 2.5:
                selected_palika.at[index, 'OM_rating'] = 'Low'
            elif 2.5 <= OM_percent < 5.0:
                selected_palika.at[index, 'OM_rating'] = 'Medium'
            elif 5.0 <= OM_percent < 10.0:
                selected_palika.at[index, 'OM_rating'] = 'High'
            else:
                selected_palika.at[index, 'OM_rating'] = 'Very High'

            # Classification of Total Nitrogen (TN %)
            if TN_percent < 0.05:
                selected_palika.at[index, 'TN_rating'] = 'Very low'
            elif 0.05 <= TN_percent < 0.1:
                selected_palika.at[index, 'TN_rating'] = 'Low'
            elif 0.1 <= TN_percent < 0.2:
                selected_palika.at[index, 'TN_rating'] = 'Medium'
            elif 0.2 <= TN_percent < 0.4:
                selected_palika.at[index, 'TN_rating'] = 'High'
            else:
                selected_palika.at[index, 'TN_rating'] = 'Very High'

            # Classification of P2O5 kg/ha
            if P2O5_kg_ha < 10:
                selected_palika.at[index, 'P2O5_rating'] = 'Very low'
            elif 10 <= P2O5_kg_ha < 30:
                selected_palika.at[index, 'P2O5_rating'] = 'Low'
            elif 30 <= P2O5_kg_ha < 55:
                selected_palika.at[index, 'P2O5_rating'] = 'Medium'
            elif 55 <= P2O5_kg_ha < 110:
                selected_palika.at[index, 'P2O5_rating'] = 'High'
            else:
                selected_palika.at[index, 'P2O5_rating'] = 'Very High'

            # Classification of K2O kg/ha
            if K2O_kg_ha < 56:
                selected_palika.at[index, 'K2O_rating'] = 'Very low'
            elif 56 <= K2O_kg_ha < 112:
                selected_palika.at[index, 'K2O_rating'] = 'Low'
            elif 112 <= K2O_kg_ha < 280:
                selected_palika.at[index, 'K2O_rating'] = 'Medium'
            elif 280 <= K2O_kg_ha < 504:
                selected_palika.at[index, 'K2O_rating'] = 'High'
            else:
                selected_palika.at[index, 'K2O_rating'] = 'Very High'

            # Classification of Boron (ppm)
            if Boron_ppm < 0.4:
                selected_palika.at[index, 'Boron_rating'] = 'Very low'
            elif 0.4 <= Boron_ppm < 0.7:
                selected_palika.at[index, 'Boron_rating'] = 'Low'
            elif 0.7 <= Boron_ppm < 1.2:
                selected_palika.at[index, 'Boron_rating'] = 'Medium'
            elif 1.2 <= Boron_ppm < 2.0:
                selected_palika.at[index, 'Boron_rating'] = 'High'
            else:
                selected_palika.at[index, 'Boron_rating'] = 'Very High'

            # Classification of Zinc (ppm)
            if Zinc_ppm < 0.5:
                selected_palika.at[index, 'Zinc_rating'] = 'Very low'
            elif 0.5 <= Zinc_ppm < 1.0:
                selected_palika.at[index, 'Zinc_rating'] = 'Low'
            elif 1.0 <= Zinc_ppm < 3.0:
                selected_palika.at[index, 'Zinc_rating'] = 'Medium'
            elif 3.0 <= Zinc_ppm < 6.0:
                selected_palika.at[index, 'Zinc_rating'] = 'High'
            else:
                selected_palika.at[index, 'Zinc_rating'] = 'Very High'

    return selected_palika

# give the dataframe argument to the function 
classify_domain_nutrients(gdf_sp)

# Define the full set of categories and corresponding colors 

categories = ['Very Low', 'Low', 'Medium','High', 'Very High']

rating_colors = {
    'Very Low' : '#FF0000', 
    'Low': '#FF6666', 
    'Medium':'#FFFFFF',
    'High': '#66FF66', 
    'Very High': '#008000'
}

#Create a ListedColormap from the colors and categories 

cmap = mcolors.ListedColormap([rating_colors[cat] for cat in categories])

# List of properties to plot 
properties = ['TN_rating', 'P2O5_rating','K2O_rating']

#create subplots 
fig , axes = plt.subplots(nrows = 3, ncols = 1, figsize = (20,15) )

for ax, prop in zip ( axes.flatten(), properties): 
    gdf_sp.plot (
    column = prop,
    legend = True,
    # legend_kwds={'labels': categories, 'loc': 'lower left', 'fontsize': 10},   
    cmap = cmap, 
    ax  = ax 
    )
    ax.set_title(f"{prop.replace('_', ' ')}",  fontsize = 15, pad = 15)
    nepal_dist.plot(ax = ax, facecolor = "none" , edgecolor = 'black')

# #adjust layout 
# plt.tight_layout

#show plot 
plt.show()

# Drop the geometry column
nepal_dist_no_geom = nepal_dist.drop(columns='geometry')

# Export to CSV
nepal_dist_no_geom.to_csv('DSM_nutrient_supply.csv', index=False)



from config import ee, ASSETS, math

# FUNCTION TO COLLECT PARAMETER INFOS
def build_parameter_stack():
    # LOAD ASSETS
    rainfall = ee.Image(ASSETS + "RainfallMonthly_Agats_2025")
    climate = ee.Image(ASSETS + "climate_era5_monthly_2025")
    dem = ee.Image(ASSETS + "DEM_Agats_SRTM90")
    soil = ee.Image(ASSETS + "SoilGrids_Topsoil_Agats")

    # DEM: ELEVATION & SLOPE PERCENTAGE
    elevation = dem.select([0]).rename("elevation")
    slope_pct = (ee.Terrain.slope(dem).multiply(math.pi).divide(180).tan().multiply(100).rename("slope_pct")
    ).rename("slope_pct")

    # ANNUAL TEMPERATURE
    temperature = (
        climate.select([
            'Temp_Jan','Temp_Feb','Temp_Mar','Temp_Apr','Temp_May','Temp_Jun',
            'Temp_Jul','Temp_Aug','Temp_Sep','Temp_Oct','Temp_Nov','Temp_Dec'
        ]).reduce(ee.Reducer.mean()).rename("Temp_Annual") 
    )

    # ANNUAL RELATIVE HUMIDITY
    humidity = (
        climate.select([
            'RH_Jan','RH_Feb','RH_Mar','RH_Apr','RH_May','RH_Jun',
            'RH_Jul','RH_Aug','RH_Sep','RH_Oct','RH_Nov','RH_Dec'
        ]).reduce(ee.Reducer.mean()).rename("RH_Annual")
    )

    # ANNUAL RAINFALL
    rainfall_annual = (
        rainfall.select([
            'Januari','Februari','Maret',
            'April','Mei','Juni',
            'Juli','Agustus','September',
            'Oktober','November','Desember'
        ]).reduce(ee.Reducer.sum()).rename("Rainfall_Annual")
    )

    # SOIL PROPERTIES
    cec = soil.select('cec')
    cn = soil.select('soc').multiply(0.1).divide(soil.select('nitrogen').multiply(0.01)).rename("cn_ratio")
    ph = soil.select('ph')
    clay = soil.select('clay').divide(10).rename("clay_pct")
    sand = soil.select('sand').divide(10).rename("sand_pct")
    silt = soil.select('silt').divide(10).rename("silt_pct")

    # COMBINE IMAGE
    stacked_image = ee.Image.cat([
        rainfall_annual,temperature,humidity,elevation,
        slope_pct,cec,cn,ph,clay,sand,silt
    ])

    return stacked_image
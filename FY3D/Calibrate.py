import numpy as np
import h5py as h5
import gdal,osr
import os

def ReadHDF(inpath,sbname):
    ds = h5.File(inpath,'r')
    arr = np.array(ds[sbname],dtype=float)
    return arr

def write_hdffile(lat,lon,var_arr1,var_arr2,var_arr3,hdf_path):
    with h5.File(hdf_path, 'a') as f:
        f.create_dataset('Variable1', data=var_arr1)
        f.create_dataset('Variable2', data=var_arr2)
        f.create_dataset('Variable3', data=var_arr3)
        f.create_dataset('Latitude', data=lat)
        f.create_dataset('Longitude', data=lon)
        f.close()

def read_raster(path):
    ds = gdal.Open(path)
    data = ds.GetRasterBand(1).ReadAsArray()
    position_info = ds.GetGeoTransform()
    return data,position_info

def Write_tif_3(bnd1_arr,bnd2_arr,bnd3_arr,position_info,outputpath):
    rows,cols = bnd1_arr.shape
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(outputpath, cols, rows, 3, gdal.GDT_UInt16)
    outRaster.SetGeoTransform(position_info)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband1 = outRaster.GetRasterBand(1)
    outband1.SetNoDataValue(np.nan)
    outband1.WriteArray(bnd1_arr)
    outband1.FlushCache()
    outband2 = outRaster.GetRasterBand(2)
    outband2.SetNoDataValue(np.nan)
    outband2.WriteArray(bnd2_arr)
    outband2.FlushCache()
    outband2 = outRaster.GetRasterBand(3)
    outband2.SetNoDataValue(np.nan)
    outband2.WriteArray(bnd3_arr)
    outband2.FlushCache()
    outRaster = None

def create_vrt(exe_path,subname,data_path,vrt_path):
   result = exe_path+" -of VRT HDF5:"+data_path+"://"+subname+" "+vrt_path
   print(result)
   os.system(result)

def modify_vrt(stresult,vrt):
    myfile = open(vrt, "r")
    content = myfile.read()
    myfile.close()
    pos = content.find("<GCPList")
    if pos != -1:
        content = content[:pos] + stresult + content[pos:]
        myfile = open(vrt, "w")
        myfile.write(content)
        myfile.close()
def vrt_support(hdf):
    text = "<Metadata domain=\"GEOLOCATION\">\
    <MDI key=\"LINE_OFFSET\">1</MDI>\
    <MDI key=\"LINE_STEP\">1</MDI>\
    <MDI key=\"PIXEL_OFFSET\">1</MDI>\
    <MDI key=\"PIXEL_STEP\">1</MDI>\
    <MDI key=\"SRS\">GEOGCS[\"WGS84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9108\"]],AUTHORITY[\"EPSG\",\"4326\"]]</MDI>\
    <MDI key=\"X_BAND\">1</MDI>"
    text_Longitude ="<MDI key=\"X_DATASET\">HDF5:\""+ hdf + "\"://Longitude</MDI>"
    text_Latitude = "<MDI key=\"Y_BAND\">1</MDI><MDI key=\"Y_DATASET\">HDF5:\"" + hdf +"\"://Latitude</MDI></Metadata>"
    vrt_txt = text+text_Longitude+text_Latitude
    return vrt_txt
def geoloc(warp_path,vrt,tif):
   result = warp_path+" -te 85 75 110 85 -tr 0.00225 0.00225 -geoloc "+vrt+" "+ tif
   print(result)
   os.system(result)

def file_list(path,format):
    arr_in = []
    arr_out = []
    lists = os.listdir(path)
    for i in lists:
        if i.split('.')[-1] == format:
            arr_in.append(path +'\\'+i)
    return arr_in

if __name__ == "__main__":
    # lon_lat_path = r"E:\Tencent\QQ_Data\1339182660\FileRecv\FY3D_MERSI_GBAL_L1_20190915_0615_GEOQK_MS.HDF"
    # bnd_path = r"E:\Tencent\QQ_Data\1339182660\FileRecv\FY3D_MERSI_GBAL_L1_20190915_0615_0250M_MS.HDF"
    # hdf_path =r'C:\Users\Zhuxw\Desktop\FY3D_MERSI_GBAL_L1_20190915_0615_GEOQK_MS_1.HDF'
    # lon = ReadHDF(lon_lat_path,'Longitude')
    # lat = ReadHDF(lon_lat_path,'Latitude')
    # bad1 = ReadHDF(bnd_path,'/Data/EV_250_RefSB_b1')
    # bad2 = ReadHDF(bnd_path, '/Data/EV_250_RefSB_b2')
    # bad3 = ReadHDF(bnd_path, '/Data/EV_250_RefSB_b3')
    # write_hdffile(lat,lon,bad1,bad2,bad3,hdf_path)

    bnd_tif1 = r'H:\Project_Data\FY_3D\TIFF\FY3D_MERSI_GBAL_L1_20190915_0615_0250M_MS_new_Variable1.tif'
    bnd_tif2 = r'H:\Project_Data\FY_3D\TIFF\FY3D_MERSI_GBAL_L1_20190915_0615_0250M_MS_new_Variable2.tif'
    bnd_tif3 = r'H:\Project_Data\FY_3D\TIFF\FY3D_MERSI_GBAL_L1_20190915_0615_0250M_MS_new_Variable3.tif'
    out_path = r'H:\Project_Data\FY_3D\TIFF\FY3D_MERSI_GBAL_L1_20190915_0615_0250M_MS.tif'
    arr1, info_po1 = read_raster(bnd_tif1)
    arr2, info_po2 = read_raster(bnd_tif2)
    arr3, info_po3 = read_raster(bnd_tif3)
    Write_tif_3(arr1, arr2, arr3, info_po1, out_path)

    # img = r'E:\Tencent\QQ_Data\1339182660\FileRecv\img'
    # geo = r'E:\Tencent\QQ_Data\1339182660\FileRecv\geo'
    # hdf_path = r'C:\Users\Zhuxw\Desktop'
    # vrt = r'C:\Users\Zhuxw\Desktop'
    # tiff = r'H:\Project_Data\FY_3D\TIFF'

    # img_arr = file_list(img,'HDF')
    # geo_arr = file_list(geo,'HDF')
    # for i in range(len(img_arr)):
    #     hdffile = hdf_path+'\\'+img_arr[i].split('\\')[-1].split('.')[0]+'_new'+'.HDF'
    #     print(hdffile)
    #     lon = ReadHDF(geo_arr[i],'Longitude')
    #     lat = ReadHDF(geo_arr[i],'Latitude')
    #     bad1 = ReadHDF(img_arr[i],'/Data/EV_250_RefSB_b1')
    #     bad2 = ReadHDF(img_arr[i], '/Data/EV_250_RefSB_b2')
    #     bad3 = ReadHDF(img_arr[i], '/Data/EV_250_RefSB_b3')
    #     write_hdffile(lat, lon, bad1, bad2, bad3, hdffile)

    # hdf = file_list(hdf_path,'HDF')
    # sub_name = ['Variable1','Variable2','Variable3']
    # for i in hdf:
    #     for j in sub_name:
    #         vrt_path = vrt + '\\' + i.split('\\')[-1].split('.')[0] + '_' + j + '.vrt'
    #         create_vrt('G:\Project\Create_raster\FY3D\gdal_translate.exe',j, i, vrt_path)
    #         coor = vrt_support(i)
    #         modify_vrt(coor, vrt_path)

    # vrt_arr = file_list(vrt,'vrt')
    # for i in vrt_arr:
    #     tif_path = tiff + '\\' + i.split('\\')[-1].split('.')[0] + '.tif'
    #     print(tif_path)
    #     geoloc('G:\Project\Create_raster\FY3D\gdalwarp.exe', i, tif_path)
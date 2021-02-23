#coding:utf-8
import os
import numpy as np
import h5py
from netCDF4 import Dataset
from util import *
import gdal

def get_mask_grid(gridpath):
    samples = 2748 
    lines = 2748
    latlon = np.fromfile(gridpath, "d")  
    latlon.resize([lines, samples, 2])  
    latlon[latlon == 999999.9999] = 0
    return latlon


def obtain_latlon(raw_path):
    latlon = get_mask_grid(raw_path)
    latlon_np = np.array(latlon)          #����ͨ�б�ת����numpy�������
    lat ,lon = np.dsplit(latlon,2)        #��numpy��ά������м�ֿ�

    latitude = np.reshape(lat,(2748,2748))
    longitude = np.reshape(lon,(2748,2748)) #����ά����ת�ɶ�ά����

    lat_split = latitude[0:2748,0:2748]   #��Ҫ�����кŷ�Χ�������޸�
    lon_split = longitude[0:2748,0:2748]
    return (latitude,longitude)


def read_ncfile(nc_path):
    """
    ��ȡnc�ļ�
    """
    nc_object = Dataset(nc_path)  #��ȡnc�ļ�����������Ϊһ������
    SSI_data = np.array(nc_object.variables['SSI']) #��ȡ��������̫����������
    SSI_data[SSI_data == -99.0]=-1
    SSI_data[SSI_data == 65532.0]=-0.5
    return SSI_data    #���ط�������


def write_hdffile(lat,lon,nc_path,hdf_path):

    Precipitation = read_ncfile(nc_path)
    with h5py.File(hdf_path, 'a') as f:
        f.create_dataset('SSI',data=Precipitation)
        f.create_dataset('Latitude', data=lat)
        f.create_dataset('Longitude', data=lon)
        f.close()  # �ر��ļ�
        
def datalists(path):
    arr = []
    lists = os.listdir(path)
    for i in lists:
        if i.split('.')[-1] == 'NC':#according to dataformat modify
            fni = path + '\\'+i
            arr.append(fni)
    return arr

def create_vrt(exe_path,data_path,vrt_path):

   result = exe_path+" -of VRT HDF5:"+data_path+"://SSI "+vrt_path
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

def geoloc(warp_path,vrt,tif):
   result = warp_path+" -te 61 1 139 57 -tr 0.04 0.04 -geoloc "+vrt+" "+ tif
   os.system(result)

#ȥ��ֵ
def eliminate_null(tif,gtif):

    rester = ReadRaster(tif)
    WriteGTiffFile(gtif,rester.nRows,rester.nCols,rester.data,rester.geotrans,65535,gdal.GDT_Float32)
    
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
     

    
if __name__=="__main__":
    raw_path = r"F:\ssi\FullMask_Grid_4000.raw" #��γ�Ȳ��ұ��·��
    nc_path = r"F:\test1"                       #nc�ļ����ڵ�Ŀ¼���������޸�
    hdf_path = r"F:\test1"                      #hdf�ļ����ڵ�Ŀ¼���������޸�
    tran_path = r"F:\FY_DATA\gdal_translate.exe" #gdal_translate.exe ·��
    vrt_path = r"F:\\test1\\"                   #vrt�ļ����ڵ�Ŀ¼���������޸�

    tif_path = r"F:\\test1\\"                        #У����tif�ļ������Ŀ¼
    warp_path = r"F:\FY_DATA\gdalwarp.exe"           #gdalwarp.exe�ļ����ڵ�·��
    gtif_path = r"F:\\dealresult\\"                 #ȥ����ֵ��gtif�ļ������·��
    
    lat,lon= obtain_latlon(raw_path) #��ȡ��γ������
    nc_list = datalists(nc_path)  #��ȡĿ¼�����е�nc�ļ�
    for i in range(len(nc_list)):
        nc = nc_list[i]
        hdf_temp = nc_list[i].split('\\')[-1].split('.')[0] + ".HDF"
        hdf = os.path.join(hdf_path,hdf_temp)
        
        vrt_temp = nc_list[i].split('\\')[-1].split('.')[0] + ".vrt"
        vrt = os.path.join(vrt_path,vrt_temp)

        tif_temp = nc_list[i].split('\\')[-1].split('.')[0] + ".tif"
        tif = os.path.join(tif_path,tif_temp)

        gtif_temp =nc_list[i].split('\\')[-1].split('.')[0] + ".tif"
        gtif = os.path.join(gtif_path,tif_temp)

        vrt_txt = vrt_support(hdf)  #��ȡ����ƴ�Ӻõ�vrt�ļ�
        
        write_hdffile(lat,lon,nc,hdf) #ͨ����γ�Ȳ��ұ��еľ�γ���������ɵĶ�ά��nc�еĽ�ˮ���ݵĶ�ά���������һ��hdf�ļ�
        create_vrt(tran_path,hdf,vrt) #ͨ��gdal_translate.exe��hdf�ļ�����һ��vrt�ļ�
        modify_vrt(vrt_txt,vrt)    #�����ɵ�vrt�ļ�����Ӹ����ַ���
        geoloc(warp_path,vrt,tif) #ͨ��vrt�ļ�����tif�ļ�
        eliminate_null(tif,gtif) #��tif�ļ�ȥ����ֵ
        
        

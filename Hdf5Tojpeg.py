import numpy as np
import h5py as h5
import cv2
import os

def ReadHDF(inpath,sbname):
    ymax = 255
    ymin = 0
    ds = h5.File(inpath,'r')
    arr = np.array(ds[sbname])
    xmax = np.max(arr)
    xmin = np.min(arr)
    bnd = (ymax - ymin) * (arr - xmin) / (xmax - xmin) + ymin
    bnd = np.round(bnd, 0).astype(int)
    return bnd
def compress_jpg(inpath,outpath):
    img = cv2.imread(inpath)
    new_image = cv2.resize(img,(2048,2000)) # acording to need modify
    cv2.imwrite(outpath,new_image)
def file_list(path):
    arr_in = []
    arr_out = []
    lists = os.listdir(path)
    for i in lists:
        if i.split('.')[-1] =='HDF':
            arr_in.append(path +'\\'+i)
            arr_out.append( path +'\\'+i.split('.')[0]+'.jpg')
    return arr_in,arr_out
def create_jpg(infilepath,outfilepath):
    bnd1 = '/Data/EV_250_RefSB_b1'
    bnd2 = '/Data/EV_250_RefSB_b2'
    bnd3 = '/Data/EV_250_RefSB_b3'
    r = ReadHDF(infilepath, bnd1)
    g = ReadHDF(infilepath, bnd2)
    b = ReadHDF(infilepath, bnd3)
    img = cv2.merge([r, g, b])
    cv2.imwrite(outfilepath,img)
if __name__ =="__main__":
    arr1,arr2 = file_list(r"C:\Users\Zhuxw\Desktop")
    for i in range(len(arr1)):
        create_jpg(arr1[i],arr2[i])
        print(arr2[i]+" has been finished.")

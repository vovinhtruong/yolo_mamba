import os
import pathlib
import time
import datetime
import random
import string
import numpy as np
import cv2

# pip install scikit-image (requires version 0.17.1 or higher)
from skimage import exposure
from skimage.filters import unsharp_mask

# ===== Settings =====
inputdirs = [
    pathlib.Path('/home/phuong/VINH_TRUONG/yolo26/dataset/graz/original_dataset/images_part1'),
    pathlib.Path('/home/phuong/VINH_TRUONG/yolo26/dataset/graz/original_dataset/images_part2'),
    pathlib.Path('/home/phuong/VINH_TRUONG/yolo26/dataset/graz/original_dataset/images_part3'),
    pathlib.Path('/home/phuong/VINH_TRUONG/yolo26/dataset/graz/original_dataset/images_part4'),
]
outputdir = pathlib.Path('/home/phuong/VINH_TRUONG/yolo26/dataset/graz/processed_dataset/images')
filetypes = set(['.tif', '.tiff', '.png', '.jpg', '.jpeg', '.bmp'])
output_filetype = '.png'
jpg_compression = '30'
outputbitdepth = 8
sharpen = False
convert_grayscale = False
equalize = True
intensity_crop = 0.05
filename_random = False
relative = False
overwrite = False

# ===== Main code =====
def get_random_alphaNumeric_string(stringLength=8):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))

def main():
    for inputdir in inputdirs:   # loop: part1..part4
        if inputdir == outputdir or not os.path.exists(inputdir):
            print(f'Error (Directory error): Please check folder path: {inputdir}')
            continue   # dont care error folder

        for paths, _, files in os.walk(os.path.normpath(inputdir), topdown=True):
            for i, file in enumerate(files, start=1):
                time_index = str(time.strftime("%H:%M:%S", time.localtime()))+' ('+str(i).zfill(8)+')'
                try:
                    filepath = os.path.join(paths, file)
                    reldir = os.path.relpath(paths, inputdir)
                    if relative == True:
                        outputpath = os.path.normpath(os.path.join(outputdir, reldir))
                    else:
                        outputpath = os.path.normpath(outputdir)
                    if filename_random == True:
                        filename = get_random_alphaNumeric_string(32)
                    else:
                        filename = file
                    if ('.' not in output_filetype):
                        output_filetype_corr = '.'+output_filetype
                    else:
                        output_filetype_corr = output_filetype
                    outputfile = os.path.normpath(pathlib.Path(os.path.join(outputpath, filename)).with_suffix(output_filetype_corr))
                    if overwrite == False and os.path.isfile(outputfile) == True:
                        print('SKIPPED (File exists), '+filepath+' - '+time_index)
                        continue
                    else:
                        if any(x in filepath.lower() for x in filetypes) == True:
                            if not os.path.exists(outputpath):
                                os.makedirs(outputpath)
                            if convert_grayscale == True:
                                img = cv2.imread(filepath, 0)
                            else:
                                img = cv2.imread(filepath, -cv2.IMREAD_ANYDEPTH)
                                pass
                            if img.dtype == 'uint16':
                                img = (img / 65535.0).astype(np.float64)
                            elif img.dtype == 'uint8':
                                img = (img / 255.0).astype(np.float64)
                            else:
                                print('ERROR (Input bit depth not supported) ,'+filepath+' - '+time_index)
                                continue
                            if equalize == True:
                                img = exposure.rescale_intensity(img, in_range=(np.percentile(img, intensity_crop), np.percentile(img, (100-intensity_crop))))
                                img = exposure.equalize_adapthist(img)
                            if sharpen == True:
                                img = unsharp_mask(img, radius=1, amount=1)
                            if outputbitdepth == 8:
                                img = cv2.normalize(img, dst=None, alpha=0, beta=int((pow(2, outputbitdepth))-1), norm_type=cv2.NORM_MINMAX).astype(np.uint8)
                            elif outputbitdepth == 16:
                                img = cv2.normalize(img, dst=None, alpha=0, beta=int((pow(2, outputbitdepth))-1), norm_type=cv2.NORM_MINMAX).astype(np.uint16)
                            else:
                                print('ERROR (Output bit depth not supported) ,'+filepath+' - '+time_index)
                                continue
                            if (('jpg' or 'jpeg') in output_filetype.lower()) and jpg_compression:
                                cv2.imwrite(str(outputfile), img, [cv2.IMWRITE_JPEG_QUALITY, int(jpg_compression)])
                                print('SUCCESS (Conversion succeeded), '+filepath+' - '+time_index)
                            else:
                                cv2.imwrite(str(outputfile), img)
                                print('SUCCESS (Conversion succeeded), '+filepath+' - '+time_index)
                except Exception as e:
                    print('ERROR (Conversion failed), '+filepath+' - '+time_index+' - '+str(e))

if __name__ == "__main__":
    main()
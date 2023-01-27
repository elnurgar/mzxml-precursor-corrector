# Precursor corrector for mzXML
## Problem
In Data-Dependent Analysis on some high resolution mass spectrometry instruments, the precursor ion m/z value doesn't perfectly correspond to the ion from MS1 spectra retained for the fragmentation.
As shown in this exemple:
![This is an image](/doc/MS1.PNG)
![This is an image](/doc/MS1_zoom.PNG)

The MS1 scan shows the presence of 332.2201, 337.1059 and 843.3971. This ions were retained for the further fragmentation to generate MS2 spectra.

When we look the values of precursor ions in mzXML file for the next scans here is what we have:
![This is an image](/doc/MS2.PNG)

The value for 332.2201 is 332.2430, for 337.1059 is 337.1240 and for 843.3971 is 843.5640, either 69, 54 and 198 ppm error. For some scans the error can achieve 500 ppm.

##Instruments concerned
The instruments where this problem is observed are:
Water Synapt G2Si - 50-800 ppm
Bruker Impact II - 50-70 ppm


##Solution
This script will fix the precursor values in mzXML files. Works with mzXML 2.1 and 3.0 (32 and 64 bit)

The steps to fix the problem are:
1) Put the executable in the same folder with mzXML files to be fixed.
![Step1](/doc/Step1.PNG)

2) Run it
3) The Waters Sypant G2Si inject every 80 scans a lock mass, reference mix. Therefore, the MS1 scans of lock mass will be ignored, as the don't come from the sample. If your machine has MS1 scans only with lock mass, you can list them in this step. Therefore, the MS1 scans with this ions as the most abundant will not be retained. 
If your machine doesn't have MS1 scans with lock mass just type 0.
![Step3](/doc/Step2.PNG)
4) The script will list mzXML file to fix. If you are ok type Y.
![Step4](/doc/Step3.PNG)

5) The script will fix mzXML data file after file.
![Step5](/doc/Step4.PNG)

6) The script will generate for each mzXML to be fixed, new mzXML called _modified with fixed precursor values.
![Step6](/doc/Step5.PNG)

7) At the same time for each mzXML file the script will generate a csv file with MS1 scan number, MS2 scan number, MS2 precursor old m/z value, MS2 precursor new m/z value, Score and Rank
![Step7](/doc/Step6.PNG)

Score is calculated by division of log2 of intensity value on the error in ppm
The rank means that this ion is the nth ion the most intense of MS1 spectra. 

8) For all files, fixed in the same batch one file log.txt is generated with the file name, and correspoding scan number with the highest error and highest rank.
![Step8](/doc/Step7.PNG)

9) Check it. All the values are fixed.
![Step9](/doc/MS2_OK.PNG)

##Citation
If you use this script please cite : Breaud, C.; Lallemand, L.; Mares, G.; Mabrouki, F.; Bertolotti, M.; Simmler, C.; Greff, S.; Mauduit, M.; Herbette, G.; Garayev, E.; Lavergne, C.; Cesari, M.; Bun-Llopet, S.-S.; Baghdikian, B.; Garayev, E. LC-MS Based Phytochemical Profiling towards the Identification of Antioxidant Markers in Some Endemic Aloe Species from Mascarene Islands. Antioxidants 2023, 12, 50. https://doi.org/10.3390/antiox12010050

##Contribution
All the contributions are welcome. Feel free to contact: elnur.garayev@univ-amu.fr

##License
MIT License

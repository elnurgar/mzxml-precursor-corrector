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

The instruments where this problem is observed are:
Water Synapt G2 - 50-800 ppm
Bruker Impact II - 50-70 ppm

This script will fix the precursor values in mzXML files. Works with mzXML 2.1 and 3.0 (32 and 64 bit)

The steps to fix the problem are:
1) Put the executable in the same folder with mzXML files to be modified.

La logique est suivante :

Pour chaque scan MS2 :

On récupère le chiffre de précurseur de mzXML original.
On récupère le spectre MS1 qui précède les scans MS2 sous forme d’un tableau mz/intensités
Pour chaque mz sur le spectre MS1 on calcule l’erreur en ppm par rapport à précurseur (50.0001, 50.0100, 50.0200 …. 1200.0010, 1200.0020)
On calcule le « score » par le rapport de log de l’intensité avec la base 2 sur l’erreur
On trie les lignes par score de plus haut vers le plus bas
On enlève les lignes avec erreur > 1000 ppm
On récupère les top 10
On trie ces 10 éléments par l’intensité de plus haute vers la plus basse
On garde les top 3
On trie de nouveau par score de plus haut vers le plus bas
On retient le premier élément comme la bonne valeur du précurseur
 

A l’issue de travail le script génère 3 fichiers :

Fichier mzXML se terminant par _modified.mzXML pour chaque analyse avec les bonnes valeurs de précurseur
Fichier csv pour chaque analyse avec un tableau : le numéro de scan MS1, le numéro de scan MS2, l’ancienne valeur de précurseur, la nouvelle valeur de précurseur, score, erreur en ppm, et rank. Rank, c’est la position de cet ion dans le tableau d’intensité, soit la nouvelle valeur de précurseur est Xème ion le plus intense sur le spectre MS1.

 

Un seul fichier log.txt avec le nom de l’analyse, le scan avec l’erreur la plus importante, et le scan avec le rank le plus élevé. Par exemple, si vous avez une analyse dont un scan a une erreur de 900 ppm, ça vaut le coup de vérifier si le précurseur est bien sélectionné.

 

Il fonctionne avec les données 32 et 64 bit.

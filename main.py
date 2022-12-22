import re
from pyteomics import mzxml
from tqdm import tqdm
import numpy as np
import os


def ms1_and_ms2_extractor(filename: str, lock_mass: list):
    ms1_data = {}
    ms2_data = {}
    ms1scans_lock_mass_list = []
    ms1_scans_list = []
    with mzxml.read(filename) as reader:
        for i in tqdm(reader, desc=filename):
            if str(i['msLevel']) == '1':
                ms1_scans_list.append(i['num'])
                a = np.vstack((i['m/z array'], i['intensity array'])).T
                for l in lock_mass:
                    back = float(l) - (float(l) * 100 / 1000000)
                    front = float(l) + (float(l) * 100 / 1000000)
                    temp_a = a[((a[:, 0] > back))]
                    temp_a = temp_a[((temp_a[:, 0] < front))]
                    if len(temp_a) > 0:
                        temp_a = temp_a[((temp_a[:, 1] > 50000))]
                        if len(temp_a) > 0:
                            ms1scans_lock_mass_list.append(i['num'])
                            # with open("test.txt", "a") as file:
                            #     file.write(f"{str(i['num'])}")
                            #     file.write("\n")
                            #     #np.savetxt(file, temp_a[:,:])
                        else:
                            ms1_data.update({i['num']: a[a[:, 1].argsort()][::-1]})
                    else:
                        ms1_data.update({i['num']: a[a[:, 1].argsort()][::-1]})

            elif str(i['msLevel']) == '2':
                ms2_data.update({i['num']: i['precursorMz'][0]['precursorMz']})

        total_spectra_no = i['num']
        print(f"Found {total_spectra_no} spectra in {filename}")
        # Return ms1_data list with [scan number, mslevel, mslist for ms1] and ms2_data list with [scan number, msLevel and ms2 precursor mz for ms2]
        return [ms1_data, ms2_data, total_spectra_no, ms1scans_lock_mass_list, ms1_scans_list]


def best_score_finder(ms1_array, precursor_mz_score, scan_number: int):
    precursor_mz = float(precursor_mz_score)
    column0 = ms1_array[:, 0:1]
    column2 = ms1_array[:, 1:2]
    # calcul pour la colonne d'erreur
    error_column = abs((precursor_mz - column0) / precursor_mz * 1000000) + 0.00001
    # ajout de la colonne sur array
    ms1_array = np.hstack((ms1_array, error_column))
    # calcul de score
    score_column = (np.log2(column2)) / error_column
    # ajout de colonne de score sur array
    score_array = np.hstack((ms1_array, score_column))

    score_array = np.flip(score_array[score_array[:, 3].argsort()], axis=0)
    # Toute erreur > 1000 est eliminé
    new_score_array = score_array[((score_array[:, 2] < 1000))]
    if len(new_score_array) > 0:
        new_score_array = new_score_array[:10, :]
    else:
        new_score_array = score_array
        print(f"ATTENTION, SCAN NUMBER {scan_number} HAS AN ERROR MORE THAN 1000 PPM!!!")

    # trier par intensité de plus haut vers plus bas. celui en 3ère positions seront retenus pour la suite
    new_score_array = np.flip(new_score_array[new_score_array[:, 1].argsort()], axis=0)
    new_new_score_array = new_score_array[:3, :]
    # trier par score. Celui en 1ère position sera retenu pour le rendu
    new_new_score_array = np.flip(new_new_score_array[new_new_score_array[:, 1].argsort()], axis=0)

    # trier par intensité de plus haut vers plus bas de ms1 spectre complet pour rank
    score_array = np.flip(score_array[score_array[:, 1].argsort()], axis=0)

    # recherche de la position du precurseur sur le spectre ms1
    rank = np.where(score_array == float(new_new_score_array[0][0]))
    # +1 car indice de premier element est 0
    rank = rank[0] + 1
    # return new mz, score, error, rank
    return new_new_score_array[0][0], new_new_score_array[0][3], new_new_score_array[0][2], rank[0]


def ms_data_processor(filename, lock_mass):
    ms_data = ms1_and_ms2_extractor(filename, lock_mass)
    ms1_data = ms_data[0]
    ms2_data = ms_data[1]
    ms1scans_lock_mass_list = ms_data[3]
    ms1_scans_list = ms_data[4]
    ms2_error = {}
    ms2_rank = {}
    ms2_result = {}
    total_spectra = int(ms_data[2])
    with open(f'{filename[:-6]}.csv', 'w', encoding='utf-8') as file:
        file.write('MS1 Scan num,MS2 Scan num,Old precursor mz,New precursor mz,Score,Error,Rank\n')
    ms1_scans_wo_lm = [scan for scan in ms1_scans_list if scan not in ms1scans_lock_mass_list]
    ms1scans_lock_mass_list = list(set(ms1scans_lock_mass_list))
    lock_mass_ms1 = []
    for i in tqdm(range(1, total_spectra), desc=filename):

        # look if is in lock mass list
        if str(i) in ms1scans_lock_mass_list:
            continue
        elif str(i) in ms1_scans_wo_lm:
            lock_mass_ms1.append(str(i))

        elif str(i) in ms2_data.keys():
            lock_mass = lock_mass_ms1[-1]
            result = best_score_finder(ms1_data[lock_mass], ms2_data[str(i)], i)
            with open(f'{filename[:-6]}.csv', 'a', encoding='utf-8') as file:
                file.write(
                    f'{lock_mass},{i},{ms2_data[str(i)]},{result[0]},{result[1]},{result[2]:.2f},{result[3]}\n')
                ms2_result[i] = result[0]
                ms2_error[i] = result[2]
                ms2_rank[i] = result[3]
        else:
            break

    highest_error = {max(ms2_error, key=ms2_error.get): ms2_error[max(ms2_error, key=ms2_error.get)]}
    highest_rank = {max(ms2_rank, key=ms2_rank.get): ms2_rank[max(ms2_rank, key=ms2_rank.get)]}
    # returns dictionnary{scannum:bon mz}, erorr, rank
    return ms2_result, highest_error, highest_rank, ms_data[0]


def slicer(filename):
    with open(filename) as file:
        line_list = file.readlines()
    return line_list


def file_writer(filename, line_list, ms2_data):
    log.append(f'{filename},{ms2_data[1]},{ms2_data[2]}\n')
    # ms2 data returns dictionnary{scannum:bon mz}, score, erorr, rank
    with open(filename[0:-6] + "_modified.mzXML", "w", encoding="utf-8") as file:
        print(f"Writing to {filename[0:-6]}_modified.mzXML")
        for line in tqdm(line_list, desc=filename):
            if "scan num=" in line:
                scan_num = re.search('scan num="(.*?)"', line)
                if int(scan_num.group(1)) in ms2_data[0].keys():
                    ms2_precursor = ms2_data[0][int(scan_num.group(1))]
                file.write(line)
            elif "precursorMz" in line:
                file.write(str(line.split('">')[0] + '">' + str(ms2_precursor) + "</precursorMz>"))
            else:
                file.write(line)


line = ''
filename = ""
results = []
results2 = []
log = []
log.append(f'Filename,Scannum:Highest error,Scannum:Highest rank in MS1 spectra\n')
for folder in ".":
    for file in os.listdir(folder):
        if file.endswith('.mzXML') and file.endswith('_modified.mzXML') != True:
            results.append(file)
lock_mass = input(
    "Please, insert your lock mass m/z as list (example: 554.2615, 556.2771. If you want to keep example values press Enter without values, if you don't want t use lock mass type 0):")
if lock_mass == "":
    lock_mass = [554.2615, 556.2771]
else:
    [x.strip() for x in lock_mass.split(',')]
print("Here are the files I have found:")
print(*results, sep="\n")
ask = input("Do you want to continue? Y or N : ")
if ask.upper() == "Y":
    for folder in ".":
        for f in os.listdir(folder):
            if f.endswith('.csv') or f.endswith('_modified.mzXML'):
                results2.append(f)
    print(*results2, sep="\n")
    if bool(results2) != False:
        ask2 = input("mzXML have been already found. Can I erase them ? Y or N : ")
        if ask2.upper() == "Y":
            for f in os.listdir(folder):
                if f.endswith('.csv'):
                    os.remove(f)
                elif f.endswith('_modified.mzXML'):
                    os.remove(f)
            for filename in results:
                print("Treating " + filename)
                line_list = slicer(filename)
                ms2_data = ms_data_processor(filename, lock_mass)
                ms1_data = ms2_data[3]
                file_writer(filename, line_list, ms2_data)
        elif ask2.upper() == "N":
            print("I understand, I don't touch them.")
        else:
            print("I don't understand you!")
    else:
        for filename in results:
            print("Treating " + filename)
            line_list = slicer(filename)
            ms2_data = ms_data_processor(filename, lock_mass)
            ms1_data = ms2_data[3]
            file_writer(filename, line_list, ms2_data)
    with open("log.txt", "w") as logfile:
        for item in log:
            logfile.write(item)

elif ask.upper() == "N":
    print("You don't want? Ok")
else:
    print("I don't understand!")

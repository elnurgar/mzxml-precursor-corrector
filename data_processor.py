from ms_extractor import ms1_and_ms2_extractor
from tqdm import tqdm
from score_finder import best_score_finder
import sys


#TODO find the error first in this script
def ms_data_processor(filename, ms1_scan_no, filetype:str, maximal_error:int):
    ms_data = ms1_and_ms2_extractor(filename, ms1_scan_no, filetype)
    ms1_data = ms_data[0]
    ms2_data = ms_data[1]
    if len(ms2_data)== 0:
        print(f"Your data file {filename} doesn't contain MS2 data. Remove this file and relaunch the script.")
        sys.exit()
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
    ft = 0 if filetype == 'mzml' else 1
    for i in tqdm(range(ft, int(total_spectra)), desc=filename):
        # look if is in lock mass list
        if str(i) in ms1scans_lock_mass_list:
            continue
        elif str(i) in ms1_scans_wo_lm:
            lock_mass_ms1.append(str(i))

        elif str(i) in ms2_data.keys():
            ms1_scan_no = lock_mass_ms1[-1]
            result = best_score_finder(ms1_data[ms1_scan_no], ms2_data[str(i)], i, maximal_error)
            with open(f'{filename[:-6]}.csv', 'a', encoding='utf-8') as file:
                file.write(
                    f'{ms1_scan_no},{i},{ms2_data[str(i)]},{result[0]},{result[1]},{result[2]:.2f},{result[3]}\n')
                ms2_result[i] = result[0]
                ms2_error[i] = result[2]
                ms2_rank[i] = result[3]
        else:
            continue
    highest_error = (max(ms2_error, key=ms2_error.get), ms2_error[max(ms2_error, key=ms2_error.get)])
    highest_rank = (max(ms2_rank, key=ms2_rank.get), ms2_rank[max(ms2_rank, key=ms2_rank.get)])
    # returns dictionnary{scannum:bon mz}, error, rank
    return ms2_result, highest_error, highest_rank, ms_data[0]

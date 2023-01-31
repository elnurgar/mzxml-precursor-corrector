from pyteomics import mzxml, mzml
from tqdm import tqdm
import numpy as np

def ms1_and_ms2_extractor(filename: str, lock_mass: list, filetype:str):
    ms1_data = {}
    ms2_data = {}
    ms1scans_lock_mass_list = []
    ms1_scans_list = []
    if filetype == 'mzxml':
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
    elif filetype == 'mzml':
        with mzml.read(filename) as reader:
            for i in tqdm(reader, desc=filename):
                if str(i['ms level']) == '1':
                    ms1_scans_list.append(str(i['index']))
                    a = np.vstack((i['m/z array'], i['intensity array'])).T
                    for l in lock_mass:
                        back = float(l) - (float(l) * 100 / 1000000)
                        front = float(l) + (float(l) * 100 / 1000000)
                        temp_a = a[((a[:, 0] > back))]
                        temp_a = temp_a[((temp_a[:, 0] < front))]
                        if len(temp_a) > 0:
                            temp_a = temp_a[((temp_a[:, 1] > 50000))]
                            if len(temp_a) > 0:
                                ms1scans_lock_mass_list.append(str(i['index']))
                                # with open("test.txt", "a") as file:
                                #     file.write(f"{str(i['num'])}")
                                #     file.write("\n")
                                #     #np.savetxt(file, temp_a[:,:])
                            else:
                                ms1_data.update({str(i['index']): a[a[:, 1].argsort()][::-1]})
                        else:
                            ms1_data.update({str(i['index']): a[a[:, 1].argsort()][::-1]})

                elif str(i['ms level']) == '2':
                    ms2_data.update({str(i['index']): i['precursorList']['precursor'][0]['selectedIonList']['selectedIon'][0]['selected ion m/z']})

            total_spectra_no = i['index']

    print(f"Found {int(total_spectra_no) + 1} spectra in {filename}")
    # Return ms1_data list with [scan number:mslist for ms1] and ms2_data list with [scan number, msLevel and ms2 precursor mz for ms2]
    return ms1_data, ms2_data, total_spectra_no, ms1scans_lock_mass_list, ms1_scans_list


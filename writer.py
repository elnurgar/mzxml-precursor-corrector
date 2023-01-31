from tqdm import tqdm
import re

#TODO format the writer for mzML
log = [f'Filename,Scan number,Highest error,Scan number,Highest rank in MS1 spectra\n']
def file_writer(filename, line_list, ms2_data, filetype:str):
    log.append(f'{filename},{ms2_data[1][0]},{ms2_data[1][1]},{ms2_data[2][0]},{ms2_data[2][1]}\n')
    # ms2 data returns a list [(scan number, maximal error), (scan number, maximal rank)]
    if filetype == 'mzxml':
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
    elif filetype == 'mzml':
        with open(filename[0:-5] + "_modified.mzML", "w", encoding="utf-8") as file:
            print(f"Writing to {filename[0:-5]}_modified.mzML")
            for line in tqdm(line_list, desc=filename):
                if "spectrum index=" in line:
                    scan_num = re.search('spectrum index="(.*?)"', line)
                    if int(scan_num.group(1)) in ms2_data[0].keys():
                        ms2_precursor = ms2_data[0][int(scan_num.group(1))]
                    file.write(line)
                elif "isolation window target m/z" in line:
                    split_line = line.split('value="')
                    split_line[0] = split_line[0] + 'value="'
                    split_line_2 = split_line[1].split('" unitCvRef')
                    split_line[1] = '" unitCvRef' + split_line_2[1]
                    file.write(split_line[0] + str(ms2_precursor) + split_line[1])
                elif "selected ion m/z" in line:
                    split_line = line.split('value="')
                    split_line[0] = split_line[0] + 'value="'
                    split_line_2 = split_line[1].split('" unitCvRef')
                    split_line[1] = '" unitCvRef' + split_line_2[1]
                    file.write(split_line[0] + str(ms2_precursor) + split_line[1])
                else:
                    file.write(line)
    return log
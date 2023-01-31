import os
from data_processor import ms_data_processor
from writer import file_writer


def slicer(filename):
    with open(filename) as file:
        line_list = file.readlines()
    return line_list

if __name__ == "__main__":
    line = ''
    filename = ""
    results = []
    results2 = []

    for folder in ".":
        for file in os.listdir(folder):
            if file.endswith('.mzXML') and file.endswith('_modified.mzXML') != True:
                results.append(file)
            elif file.endswith('.mzML') and file.endswith('_modified.mzML') != True:
                results.append(file)
    lock_mass = input(
        "Please, insert your lock mass m/z as list (example for Waters: 554.2615, 556.2771. If you don't want t use lock mass press Enter):")
    if lock_mass == "":
        lock_mass = [0]
    else:
        lock_mass = [x.strip() for x in lock_mass.split(',')]

    print("Here are the files I have found:")
    print(*results, sep="\n")
    ask = input("Do you want to continue? Y or N : ")
    if ask.upper() == "Y":
        for folder in ".":
            for f in os.listdir(folder):
                if f.endswith('.csv') or f.endswith('_modified.mzXML') or f.endswith('_modified.mzML'):
                    results2.append(f)
        print(*results2, sep="\n")
        if bool(results2) != False:
            ask2 = input("Modified data has been already found. Can I erase them ? Y or N : ")
            if ask2.upper() == "Y":
                for f in os.listdir(folder):
                    if f.endswith('.csv'):
                        os.remove(f)
                    elif f.endswith('_modified.mzXML'):
                        os.remove(f)
                    elif f.endswith('_modified.mzML'):
                        os.remove(f)
                for filename in results:
                    print("Treating " + filename)
                    if 'MZXML' in filename.upper():
                        line_list = slicer(filename)
                        ms2_data = ms_data_processor(filename, lock_mass, 'mzxml')
                        log = file_writer(filename, line_list, ms2_data, 'mzxml')
                    elif 'MZML' in filename.upper():
                        line_list = slicer(filename)
                        ms2_data = ms_data_processor(filename, lock_mass, 'mzml')
                        log = file_writer(filename, line_list, ms2_data, 'mzml')
            elif ask2.upper() == "N":
                print("I understand, I don't touch them.")
            else:
                print("I don't understand you!")
        else:
            for filename in results:
                print("Treating " + filename)
                if 'MZXML' in filename.upper():
                    line_list = slicer(filename)
                    ms2_data = ms_data_processor(filename, lock_mass, 'mzxml')
                    log = file_writer(filename, line_list, ms2_data, 'mzxml')
                elif 'MZML' in filename.upper():
                    line_list = slicer(filename)
                    ms2_data = ms_data_processor(filename, lock_mass, 'mzml')
                    log = file_writer(filename, line_list, ms2_data, 'mzml')
        with open("log.csv", "w") as logfile:
            for item in log:
                logfile.write(item)

    elif ask.upper() == "N":
        print("You don't want? Ok")
    else:
        print("I don't understand!")

import numpy as np

def best_score_finder(ms1_array, precursor_mz_score, scan_number: int):
    precursor_mz = float(precursor_mz_score)
    #supprimer les lignes avec intensité 0
    ms1_array = ms1_array[((ms1_array[:,1] != 0))]

    column0 = ms1_array[:, 0:1]
    column2 = ms1_array[:, 1:2]
    # calcul pour la colonne d'erreur
    error_column = abs((precursor_mz - column0) / precursor_mz * 1000000) + 0.000001
    # ajout de la colonne sur array
    ms1_array = np.hstack((ms1_array, error_column))
    #divide by zero log2 erreur
    column2 = column2[((column2[:, 0] != 0))]
    # calcul de score
    score_column = np.log2(column2) / error_column
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
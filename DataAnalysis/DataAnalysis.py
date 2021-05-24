import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

def process_df(df, parameter1, parameter2, parameter3, fix_parameters):
    """Extrait les colonnes d'intérêt sous forme de listes, à partir du dataframe, des paramètres fixes et variables"""
    if parameter1 not in df.columns or parameter2 not in df.columns or parameter3 not in df.columns:
        print("\n Attention : un des paramètres (" + parameter1 + ', ' + parameter2 + ', ' + parameter3 + ") n'est pas dans le dataframe \n")
        return None
    sub_df = df
    for key in fix_parameters.keys():
        if key not in [parameter1, parameter2, parameter3]:
            sub_df = sub_df[sub_df[key] == fix_parameters[key]]
    return list(sub_df[parameter1]), list(sub_df[parameter2]), list(sub_df[parameter3])

def rule_tip(tip):
    """Associe à chaque couleur d'embout son diamètre"""
    tip_diameters = {'P':0.51, 'R':0.61, 'V':0.84, 'N':1.2, 'O':1.54}
    if tip in tip_diameters.keys():
        Dj = tip_diameters[tip]
        return Dj
    else:
        print('\n Attention : embout inconnu dans le dataframe ! \n')
        return None

def compute(df, compute_choice):
    """Calcule les grandeurs d'intérêt choisies dans compute_choice"""
    catalogue = ['Dj', 'R', 'v_on', 'v_off', 'v_lim', 'InvSinAngle', 'f_lim', 'v_orth_lim','v_on_orth', 'v_off_orth', 'v', 'RQ']
    for choice in compute_choice:
        if choice not in catalogue:
            print('\n Attention : ' + choice + ' est à calculer, mais elle ne fait pas partie du catalogue !\n')
            return None
    if 'Embout' in df.columns:
        df['Dj'] = df.apply((lambda x: rule_tip(x['Embout'])), axis=1)
    if 'R' in compute_choice:
        df['R'] = df['Dc']/df['Dj']
    if 'v_on' in compute_choice and 'Q_on' in df.columns:
        df['v_on'] = 4*df['Q_on']/(np.pi*df['Dj']**2)
    if 'v_off' in compute_choice and 'Q_off' in df.columns:
        df['v_off'] = 4*df['Q_off']/(np.pi*df['Dj']**2)
    if 'v_lim' in compute_choice:
        df['v_lim'] = 4*df['Q_lim']/(np.pi*df['Dj']**2)
    if 'Angle' in df.columns and 'InvSinAngle' in compute_choice:
        df['InvSinAngle'] = 1/np.sin(np.pi*df['Angle']/180)
    if 'f_lim' in compute_choice:
        df['f_lim'] = 2.75*df['U']
    if 'v_orth_lim' in compute_choice:
        df['v_orth_lim'] = -2*np.pi*2.75*df['U']*df['Dc']*1e-3
    if 'v_on_orth' in compute_choice and 'Q_on' in df.columns:
        df['v_on_orth'] = 4*df['Q_on']/(np.pi*df['Dj']**2)*np.sin(df['Angle']*np.pi/180)
    if 'v_off_orth' in compute_choice and 'Q_on' in df.columns:
        df['v_off_orth'] = 4*df['Q_off']/(np.pi*df['Dj']**2)*np.sin(df['Angle']*np.pi/180)
    if 'v' in compute_choice and 'Q' in df.columns:
        df['v'] = 4*df['Q']/(np.pi*df['Dj']**2)
    if 'RQ' in compute_choice:
        df['RQ'] = df['Dc']/df['Dj']*df['Q']
    return df

def labelling(parameter):
    """Donne des jolies étiquettes aux courbes"""
    label = parameter
    labels = {}
    labels['Dc'] = "Diamètre du cylindre $D_c$ (mm)"
    labels['Dj'] = "Diamètre du jet $D_j$ (mm)"
    labels['R'] = "Rapport $D_c/D_j$"
    labels['Q_on'] = "Débit d'accrochage (mL/s)"
    labels['Q_off'] = "Débit de décrochage (mL/s)"
    labels['v_on'] = "Vitesse d'accrochage (m/s)"
    labels['v_off'] = "Vitesse de décrochage (m/s)"
    labels['Angle'] = "Angle entre le jet et le cylindre (°)"
    labels['InvSinAngle'] = "Inverse du sinus de l'angle entre le jet et le cylindre"
    labels['U'] = "Tension d'alimentation du moteur (V)"
    labels['f_mes'] = "Fréquence algébrique de rotation du moteur (Hz)"
    labels['f_lim'] = "Fréquence limite de rotation (Hz)"
    labels['v_orth_lim'] = "Vitesse orthoradiale limite (m/s)"
    labels['v_on_orth'] = "Vitesse orthoradiale d'accrochage (m/s)"
    labels['v_off_orth'] = "Vitesse orthoradiale de décrochage (m/s)"
    labels['Q'] = "Débit du jet $Q$ (mL/s)"
    labels['v'] = "Vitesse du jet $v$ (m/s)"
    labels['RQ'] = "$Q D_c/D_j$ (mL/s)"
    if parameter in labels:
        label = labels[parameter]
    return label

def zeros_exterminator(x):
    """Elimine les zéros de la liste x"""
    return [item if abs(item) > 1e-3 else None for item in x]

def give_title(fix_parameters):
    """Donne un titre au graphe en fonction du ou des paramètre(s) fixés"""
    title = ''
    words = FileName[:-4].split("_")
    for word in words:
        if word == 'verre' or word == 'plastique':
            title += 'Cylindre de ' + word
        if word in ['eau', 'eausavonneuse', 'statique']:
            if word == 'eausavonneuse':
                title +=  ', eau savonneuse'
            else:
                title += ', ' + word
    for item in list(fix_parameters.keys()):
        title += ', ' + str(item) + ' = ' + str(fix_parameters[item])
    return title

def trace(df, parameter, value1, value2, fix_parameters):
    """Trace 2 grandeurs en fonction du paramètre chosisi"""
    parameters = [parameter, value1, value2] + list(fix_parameters.keys())
    compute_choice = [parameter for parameter in parameters if parameter not in df.columns]
    df = compute(df, compute_choice)

    x, y1, y2 = process_df(df, parameter, value1, value2, fix_parameters)
    y1 = zeros_exterminator(y1)
    y2 = zeros_exterminator(y2)

    plt.plot(x, y1, '.', label = labelling(value1))
    if value2 != value1:
        plt.plot(x, y2, '.', label = labelling(value2))
    plt.xlabel(labelling(parameter))
    plt.legend()
    plt.title(give_title(fix_parameters))
    plt.show()
    print(df)

def auto(df):
    """S'occupe de tout, avec des paramètres par défaut"""
    parameter = 'R'
    value1 = 'v_on'
    value2 = 'v_off'
    if FileName == 'angle.csv':
        parameter = 'Angle'
    if FileName == 'moteur.csv':
        parameter = 'U'
        value1 = 'f_mes'
        value2 = 'f_mes'
    if FileName == 'rotationdestruction.csv':
        parameter = 'v_on'
        value1 = 'v_orth_lim'
        value2 = 'v_orth_lim'
    if FileName == 'verre_eau_statique_angle.csv':
        value1 = 'v_off_orth'
        value2 = 'v_on_orth'
    trace(df, parameter, value1, value2, fix_parameters)

def lambdas(df, parameter, value, fix_parameters):
    """Trace les lambdas en fonction de 'parameter', 
    en fixant les paramètres mis dans 'fix_parameters'"""
    parameters = [parameter, value] + list(fix_parameters.keys())
    compute_choice = [parameter for parameter in parameters if parameter not in df.columns]
    df = compute(df, compute_choice)

    sub_df = df
    for key in fix_parameters.keys():
        if key!=parameter:
            sub_df = sub_df[sub_df[key] == fix_parameters[key]]
    sub_df["lambda"] = sub_df["lambda"].apply(eval)
    x, y = list(sub_df[parameter]), list(sub_df['lambda'])

    lambda1 = []
    lambda2 = []
    lambda3 = []
    lambda4 = []
    lambda5 = []
    lambda6 = []
    for item in y:
        lambda1.append(item[1])
        lambda2.append(item[2])
        if len(item) > 3:
            lambda3.append(item[3])
        else:
            lambda3.append(None)
        if len(item) > 4:
            lambda4.append(item[4])
        else:
            lambda4.append(None)
        if len(item) > 5:
            lambda5.append(item[5])
        else:
            lambda5.append(None)
        if len(item) > 6:
            lambda6.append(item[6])
        else:
            lambda6.append(None)
        
    # z = np.linspace(min(x), max(x))
    # slope1, intercept1 = linear_regression(x,lambda1)
    # reglin1 = z*slope1 + intercept1
    # slope2, intercept2 = linear_regression(x,lambda2)
    # reglin2 = z*slope2 + intercept2
    # slope3, intercept3 = linear_regression(x,lambda3)
    # reglin3 = z*slope3 + intercept3
    # slope4, intercept4 = linear_regression(x,lambda4)
    # reglin4 = z*slope4 + intercept4
    

    plt.plot(x, lambda1, '.', label = '$\lambda_1$')
    plt.plot(x, lambda2, '.', label = '$\lambda_2$')
    plt.plot(x, lambda3, '.', label = '$\lambda_3$')
    plt.plot(x, lambda4, '.', label = '$\lambda_4$')
    # plt.plot(x, lambda5, '.', label = '$\lambda_5$')
    # plt.plot(x, lambda6, '.', label = '$\lambda_6$')
    # plt.plot(z, reglin1)
    # plt.plot(z, reglin2)
    # plt.plot(z, reglin3)
    # plt.plot(z, reglin4)
    plt.xlabel(labelling(parameter))
    plt.ylabel("Distance selon l'axe z (cm)")
    plt.legend(loc='upper left', ncol=4)
    plt.title("Évolution du pas de l'hélice"+give_title(fix_parameters))
    plt.show()
    print(df)

def linear_regression(x,y):
    Y = []
    X = []
    for i in range(len(y)):
        if y[i] != None:
            Y.append(y[i])
            X.append(x[i])
    X = np.array(X).reshape((-1, 1))
    model = LinearRegression().fit(X, Y)
    slope = model.coef_
    intercept = model.intercept_
    r_sq = model.score(X, Y)
    print('coefficient of determination:', r_sq)
    print('intercept:', intercept)
    print('slope:', slope)
    return slope, intercept

## Catalogue
# Fichiers :
#               Nom                                     Paramètres disponibles
#               "verre_eau_statique.csv"                'Embout', 'Dj, 'Dc', 'R', 'Q_off', 'Q_on', 'v_off', 'v_on'
#               "plastique_eau_statique.csv"            'Embout', 'Dj, 'Dc', 'R', 'Q_off', 'Q_on', 'v_off', 'v_on'
#               "verre_eausavonneuse_statique.csv"      'Embout', 'Dj, 'Dc', 'R', 'Q_off', 'Q_on', 'v_off', 'v_on'
#               "angle.csv"                             'Embout', 'Dj, 'Dc', 'R', 'Q_off', 'Q_on', 'v_off', 'v_on', 'Angle', 'InvSinAngle'
#               "moteur.csv"                            'U', 'f_mes'
#               "rotationdestruction.csv"               'Embout', 'Dj, 'Dc', 'R', 'Q_on', 'v_on', 'U', 'f_lim', 'v_orth_lim'
#               "verre_eau_statique_angle.csv"          'Embout', 'Dj, 'Dc', 'R', 'Q_off', 'Q_on', 'v_off', 'v_on', 'v_off_orth', 'v_on_orth'
# Note : '_' est un séparateur d'informations dans le nom des fichiers

# Paramètres :
# Il s'agit de l'ensembles des paramètres contenus dans le fichier CSV et des paramètres calculés.
# 'Dc'              diamètre du cylindre en mm, parmi : 4, 6, 8, 10 en verre, 5, 8, 10 en plastique
# 'Embout'          type d'embout, parmi : 'P' (violet), 'R' (rose), 'V' (vert), 'N' (noir), 'O' (olive)
# 'Dj'              diamètre du jet. "rule_tip" s'occupe de faire la correspondance avec 'Embout' automatiquement
# 'R'               rapport Dc/Dj
# 'Q_on', 'Q_off'   débits d'accrochage et de décrochage en mL/s
# 'v_on', 'v_off'   vitesses d'accrochage et de décrochage en m/s
# 'Angle'           angle en degrés entre le jet et le cylindre
# 'InvSinAngle'     inverse du sinus de l'angle entre le jet et le cylindre
# 'U'               tension en volt aux bornes du moteur
# 'f_mes'           fréquence de rotation du moteur mesurée pour étalonnage
# 'f_lim'           fréquence de rotation du moteur calculée à partir de sa tension d'alimentation
# 'v_orth_lim'      vitesse orthoradiale limite d'un point en rotation sur le cylindre en m/s
# 'v_off_orth'      vitesse de décrochage projetée de manière orthoradiale
# 'v_on_orth'       vitesse d'accrochage projetée de manière orthoradiale


### Réglages et exécution en mode manuel
# 1) Choisir le fichier .csv à exploiter
FileName = "lambdas.csv"

df  = pd.read_csv(FileName, sep = ",")

# 2) Étape non obligatoire : définir les paramètres à fixer
# sous la forme " fix_parameters = {'paramètre1':valeur1, 'paramètre2':valeur2, ...} "
fix_parameters = {'Angle':33.5} # Ex : 'Dc':8, 'Dj':0.61

# 3) Définir quelles grandeurs tracer en fonction de quel paramètre.
# Note : Si on ne veut tracer qu'une seule grandeur, mettre deux fois la même.
paramètre = 'RQ'
grandeur1 = 'lambda'
grandeur2 = 'lambda'

# trace(df, paramètre, grandeur1, grandeur2, fix_parameters)
lambdas(df, paramètre, grandeur1, fix_parameters)

# 4) Exécuter le programme


### Mode automatique : on précise juste le nom du fichier et on laisse
# la fonction auto(df) s'occuper de tout avec des paramètres par défaut :)
# /!\ auto n'est pas conçu pour fonctionner avec lambdas

# auto(df)

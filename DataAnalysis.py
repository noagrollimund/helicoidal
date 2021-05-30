import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import naming

def process_df(df, parameter1, parameter2, parameter3, fix_parameters):
    """Extrait les colonnes d'intérêt sous forme de listes, à partir du dataframe, des paramètres fixes et variables"""
    if parameter1 not in df.columns or parameter2 not in df.columns or parameter3 not in df.columns:
        print("\n /!\ : un des paramètres (" + parameter1 + ', ' + parameter2 + ', ' + parameter3 + ") n'est pas dans le dataframe ! \n")
        return None
    sub_df = df
    for key in fix_parameters.keys():
        if key not in [parameter1, parameter2, parameter3]:
            sub_df = sub_df[sub_df[key] == fix_parameters[key]]
    if 'lambda' == parameter2:
        sub_df['lambda'] = sub_df['lambda'].apply(eval)
    if parameter2 == parameter3:
        return list(sub_df[parameter1]), list(sub_df[parameter2])
    else:
        return list(sub_df[parameter1]), list(sub_df[parameter2]), list(sub_df[parameter3])

def rule_tip(tip):
    """Associe à chaque couleur d'embout son diamètre"""
    tip_diameters = {'P':0.51, 'R':0.61, 'V':0.84, 'N':1.2, 'O':1.54}
    if tip in tip_diameters.keys():
        Dj = tip_diameters[tip]
        return Dj
    else:
        print('\n /!\ : embout inconnu dans le dataframe ! \n')
        return None

def compute(df, compute_choice):
    """Calcule les grandeurs d'intérêt choisies dans compute_choice"""
    catalogue = ['Dj', 'R', 'v_on', 'v_off', 'v_lim', 'InvSinAngle', 'f_lim', 'v_orth_lim','v_on_orth', 'v_off_orth', 'v', 'RQ', 'QR']
    for choice in compute_choice:
        if choice not in catalogue:
            print('\n /!\ : ' + choice + ' est à calculer, mais cette grandeur ne fait pas partie du catalogue !\n')
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
    if 'QR' in compute_choice:
        df['QR'] = df['Dc']/df['Dj']*df['Q']
    return df

def zeros_exterminator(x):
    """Elimine les zéros de la liste x"""
    return [item if abs(item) > 1e-3 else None for item in x]

def coiling(df, parameter, value1, value2, fix_parameters):
    """Trace 2 grandeurs en fonction du paramètre chosisi"""
    if parameter == '' or value1 == '' or value2 == '':
        print("\n /!\ : Un paramètre ou une grandeur n'a pas été choisi ! \n")
        return None
    parameters = [parameter, value1, value2] + list(fix_parameters.keys())
    compute_choice = [parameter for parameter in parameters if parameter not in df.columns]
    df = compute(df, compute_choice)
    if value1 == value2:
        x, y1 = process_df(df, parameter, value1, value2, fix_parameters)
    else:
        x, y1, y2 = process_df(df, parameter, value1, value2, fix_parameters)
        y2 = zeros_exterminator(y2)
    y1 = zeros_exterminator(y1)

    plt.plot(x, y1, '.', label = naming.labelling(value1))
    if value2 != value1:
        plt.plot(x, y2, '.', label = naming.labelling(value2))
    plt.xlabel(naming.labelling(parameter))
    plt.legend()
    plt.title(naming.give_title(FileName, fix_parameters))
    plt.show()
    print('\n Dataframe final \n', df)

def linear_regression(x,y):
    """Calcule la régression linéaire à partir de la donnée de x et y"""
    X, Y = [], []
    for i in range(len(y)):
        if y[i] != None:
            Y.append(y[i])
            X.append(x[i])
    X = np.array(X).reshape((-1, 1))
    model = LinearRegression().fit(X, Y)
    return model.coef_, model.intercept_

def lambda_organizer(y, n):
    """Réarrange les listes de listes de lambdas"""
    all_lambdas = [[] for k in range(n)]
    for item in y:
        for i in range(n):
            if len(item) > i+1:
                all_lambdas[i].append(item[i+1])
            else:
                all_lambdas[i].append(None)
    return all_lambdas

def lambdas(df, parameter, fix_parameters, n, reglin = False):
    """Trace les lambdas en fonction de 'parameter', en fixant les paramètres mis dans 'fix_parameters'"""
    if parameter == '':
        print("\n /!\ : Aucun paramètre n'a été choisi ! \n")
        return None
    parameters = [parameter, 'lambda'] + list(fix_parameters.keys())
    compute_choice = [parameter for parameter in parameters if parameter not in df.columns]
    df = compute(df, compute_choice)
    x, y = process_df(df, parameter, 'lambda', 'lambda', fix_parameters)
    lambdas = lambda_organizer(y, n)
    
    lbd_labels = ['$\lambda_1$', '$\lambda_2$', '$\lambda_3$', '$\lambda_4$', '$\lambda_5$', '$\lambda_6$']
    for i in range(n):
        plt.plot(x, lambdas[i], '.', label = lbd_labels[i])
    
    if reglin:
        z = np.linspace(min(x), max(x))
        slopes, intercepts, reglins = [[] for k in range(n)], [[] for k in range(n)], []
        for i in range(n):
            slopes[i], intercepts[i] = linear_regression(x, lambdas[i])
            reglins.append(list(z*slopes[i]+intercepts[i]))
            plt.plot(z, reglins[i])
        
    plt.xlabel(naming.labelling(parameter))
    plt.ylabel("Distance selon l'axe z (cm)")
    plt.legend(loc = 'upper left', ncol = 4)
    plt.title("Évolution du pas de l'hélice" + naming.give_title(FileName, fix_parameters))
    plt.show()
    print('\n Dataframe final \n', df)

def auto(df):
    """S'occupe de tout, avec des paramètres par défaut"""
    if FileName == 'lambdas.csv':
        lambdas(df, 'RQ', {'Angle':33.5}, 4, True)
    else:
        parameter, value1, value2 = 'R', 'v_on', 'v_off'
        fix_parameters = {}
        if FileName == 'angle.csv':
            parameter = 'Angle'
        if FileName == 'moteur.csv':
            parameter, value1, value2 = 'U', 'f_mes', 'f_mes'
        if FileName == 'rotationdestruction.csv':
            parameter, value1, value2 = 'v_on', 'v_orth_lim', 'v_orth_lim'
        if FileName == 'verre_eau_statique_angle.csv':
            value1, value2 = 'v_off_orth', 'v_on_orth'
        coiling(df, parameter, value1, value2, fix_parameters)



########################################################################################################
### Partie du code à modifier pour utiliser le programme ###
# Note : Les fichiers et paramètres disponibles sont listés dans la partie Catalogue, à la fin du code.

if __name__ == "__main__" :
    ### Mode automatique : activer le mode auto (AutoMode = True) et préciser le nom du fichier.
    # La fonction auto(df) s'occupe de tout avec des paramètres par défaut !
    AutoMode = False

    ### OU ###

    ### Mode manuel :
    # 1) Choisir le fichier .csv à exploiter (changer la valeur de 'FileName')
    FileName = "lambdas.csv"

    # 2) Étape facultative : définir les paramètres à fixer
    # sous la forme "fix_parameters = {'paramètre1':valeur1, 'paramètre2':valeur2, ...}"
    fix_parameters = {'Angle':33.5} # Exemple : fix_parameters = {'Angle':33.5, 'Dc':8, 'Dj':0.61}

    # 3) Définir quelles grandeurs tracer en fonction de quel paramètre.
    # Notes :   - Pour les lambdas, la grandeur est forcément 'lambda' et n'a pas besoin d'être définie.
    #           - Si on ne veut tracer qu'une seule grandeur, mettre deux fois la même.
    paramètre = 'RQ'
    grandeur1 = ''
    grandeur2 = ''

    # 4) Pour 'lambdas.csv' seulement : préciser le nombre n de longueurs d'onde à tracer et si on veut une régression linéaire.
    n = 4
    reglin = True

    # 5) Exécuter le programme
#########################################################################################################


#########################################################################################################
    ### Ne pas modifier ###
    df  = pd.read_csv(FileName, sep = ",")
    if AutoMode:
        auto(df)
    else:
        if FileName == 'lambdas.csv':
            lambdas(df, paramètre, fix_parameters, n, reglin)
        else:
            coiling(df, paramètre, grandeur1, grandeur2, fix_parameters)
#########################################################################################################


""" Catalogue
Fichiers :
              Nom                                     Paramètres disponibles
              "verre_eau_statique.csv"                'Embout', 'Dj, 'Dc', 'R', 'Q_off', 'Q_on', 'v_off', 'v_on'
              "plastique_eau_statique.csv"            'Embout', 'Dj, 'Dc', 'R', 'Q_off', 'Q_on', 'v_off', 'v_on'
              "verre_eausavonneuse_statique.csv"      'Embout', 'Dj, 'Dc', 'R', 'Q_off', 'Q_on', 'v_off', 'v_on'
              "angle.csv"                             'Embout', 'Dj, 'Dc', 'R', 'Q_off', 'Q_on', 'v_off', 'v_on', 'Angle', 'InvSinAngle'
              "moteur.csv"                            'U', 'f_mes'
              "rotationdestruction.csv"               'Embout', 'Dj, 'Dc', 'R', 'Q_on', 'v_on', 'U', 'f_lim', 'v_orth_lim'
              "verre_eau_statique_angle.csv"          'Embout', 'Dj, 'Dc', 'R', 'Q_off', 'Q_on', 'v_off', 'v_on', 'v_off_orth', 'v_on_orth'
              "lambdas.csv"                           'Angle', 'Dj', 'Dc', 'Q', 'lambda', 'v', 'RQ'
Note : '_' est un séparateur d'informations dans le nom des fichiers

Paramètres :
Il s'agit de l'ensembles des paramètres contenus dans les fichiers CSV et des paramètres calculés.
'Dc'              diamètre du cylindre en mm, parmi : 4, 6, 8, 10 en verre, 5, 8, 10 en plastique
'Embout'          type d'embout, parmi : 'P' (violet), 'R' (rose), 'V' (vert), 'N' (noir), 'O' (olive)
'Dj'              diamètre du jet. "rule_tip" s'occupe de faire la correspondance avec 'Embout' automatiquement
'R'               rapport Dc/Dj
'Q_on', 'Q_off'   débits d'accrochage et de décrochage en mL/s
'v_on', 'v_off'   vitesses d'accrochage et de décrochage en m/s
'Angle'           angle en degrés entre le jet et le cylindre
'InvSinAngle'     inverse du sinus de l'angle entre le jet et le cylindre
'U'               tension en volt aux bornes du moteur
'f_mes'           fréquence de rotation du moteur mesurée pour étalonnage
'f_lim'           fréquence de rotation du moteur calculée à partir de sa tension d'alimentation
'v_orth_lim'      vitesse orthoradiale limite d'un point en rotation sur le cylindre en m/s
'v_off_orth'      vitesse de décrochage projetée de manière orthoradiale
'v_on_orth'       vitesse d'accrochage projetée de manière orthoradiale
'v'               vitesse du jet (pour les lambdas)
'RQ'              produit du débit par le rapport R (fonctionne aussi si on demande 'QR')
'lambda'          liste des demi-longueurs d'onde successives
"""
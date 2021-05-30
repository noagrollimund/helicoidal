def labelling(parameter):
    """Donne des étiquettes aux courbes"""
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
    labels['QR'] = "$Q D_c/D_j$ (mL/s)"
    if parameter in labels:
        label = labels[parameter]
    return label

def give_title(FileName, fix_parameters):
    """Donne un titre au graphe en fonction du ou des paramètre(s) fixés et du nom du fichier"""
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
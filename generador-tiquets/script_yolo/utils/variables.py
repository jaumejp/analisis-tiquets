import numpy as np

ud = {
    'quantitat_ud': {'left': 25, 'width': 40},
    'descripcio': {'left': 65, 'width': 200},
    'preu_unitari': {'left': 307.5, 'width': 70},
    'import': {'left': 430,  'width': 45},
}

kg = {
    'quantitat_kg': {'left': 99, 'width': 60},
    'descripcio': {'left': 65, 'width': 200},
    'preu_unitari': {'left': 307.5, 'width': 70},
    'import': {'left': 430,  'width': 45},
}

total = {
    'total': {'left': 400,  'width': 75},
}

ud_cropped = {
  'quantitat_ud': {'left': 25-25, 'width': 40},
  'descripcio': {'left': 65-25, 'width': 200},
  'preu_unitari': {'left': 307.5-25, 'width': 70},
  'import': {'left': 430-25,  'width': 45},
}

kg_cropped = {
    'quantitat_kg': {'left': 99-25, 'width': 60},
    'descripcio': {'left': 65-25, 'width': 200},
    'preu_unitari': {'left': 307.5-25, 'width': 70},
    'import': {'left': 430-25,  'width': 45},
}

total_cropped = {
    'total': {'left': 400-25,  'width': 75},
}

escala_ponderacio = {
    'Cura facial i corporal': 0.01,
    'Neteja i llar': 0.01,
    'Forn i pastisseria': 0.01,
    'Celler': 0.01,
    'Congelats': 0.225,
    'Xarcuteria i formatges': 0.07,
    'Carn': 0.06,
    'Postres i iogurts': 0.06,
    'Cura dels cabells': 0.01,
    'Maquillatge': 0.01,
    'Conserves, brous i cremes': 0.015,
    'Marisc i peix': 0.01,
    'Aigua i refrescos': 0.06,
    'Sucre, caramels i xocolata': 0.015,
    'Nadó': 0.01,
    'Cacau, cafè i infusions': 0.01,
    'Oli, espècies i salses': 0.06,
    'Fruita i verdura': 0.225,
    'Aperitius': 0.01,
    'Ous, llet i mantega': 0.06,
    'Pizzes i plats preparats': 0.01,
    'Cereals i galetes': 0.01,
    'Arròs, llegums i pasta': 0.06,
    'Mascotes': 0.015,
    'Sucs': 0.015,
    'Fitoteràpia i parafarmàcia': 0.01,
}

dtype_dict = {
    'category': str,
    'subcategory': str,
    'name': str,
    'iva': str,
    'bulk_price': float,
    'unit_price': float,
    'units': float,
    'format': str,
    'image': str,
}

cards = np.array([
    {'targeta_1': 'VISA CREDITO/DEB', 'targeta_2': 'Visa CaixaBank'},
    {'targeta_1': 'Mastercard', 'targeta_2': 'Mastercard'},
    {'targeta_1': 'American Express', 'targeta_2': 'American Express'},
    {'targeta_1': 'Discover', 'targeta_2': 'Discover'},
    {'targeta_1': 'Maestro', 'targeta_2': 'Maestro'},
    {'targeta_1': 'Diners Club', 'targeta_2': 'Diners Club'},
    {'targeta_1': 'JCB', 'targeta_2': 'JCB'},
    {'targeta_1': 'UnionPay', 'targeta_2': 'UnionPay'},
    {'targeta_1': 'Mir', 'targeta_2': 'Mir'},
    {'targeta_1': 'Elo', 'targeta_2': 'Elo'},
    {'targeta_1': 'RuPay', 'targeta_2': 'RuPay'},
    {'targeta_1': 'Hipercard', 'targeta_2': 'Hipercard'}
])

cards_weights = np.array([25, 25, 25, 1, 1, 1, 1, 1, 1, 1, 1, 1])

cat = ['GIRONA', 'BARCELONA', 'LLEIDA', 'TARRAGONA']

__all__ = ['ud', 'kg', 'total', 'ud_cropped', 'kg_cropped', 'total_cropped', 'escala_ponderacio', 'cards', 'cards_weights', 'cat', 'dtype_dict']
import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

def valid_tikets_input(valor):   
    try: 
        valor_int = int(valor)
        if valor_int <= 0:
            raise argparse.ArgumentTypeError(f"{valor} no és un valor vàlid, ha de ser més gran que 0.")
        if valor_int > 100000:
            raise argparse.ArgumentTypeError(f"{valor} no és un valor vàlid, ha de ser més petit que 100000")
        return valor_int
    except ValueError:
        raise argparse.ArgumentTypeError(f"{valor} no és un valor vàlid, ha de ser un valor enter")

def valid_products_input(valor):
    try: 
        valor_int = int(valor)
        if valor_int <= 0:
            raise argparse.ArgumentTypeError(f"{valor} no és un valor vàlid, ha de ser més gran que 0.")
        if valor_int > 10:
            raise argparse.ArgumentTypeError(f"{valor} no és un valor vàlid, ha de ser més petit que 10")
        return valor_int
    except ValueError:
        raise argparse.ArgumentTypeError(f"{valor} no és un valor vàlid, ha de ser un valor enter")

def valid_lvl_input(valor):
    try:
        valor_int = int(valor)
        if valor_int not in [0, 1, 2, 3, 4, 5]:
            raise argparse.ArgumentTypeError(f"{valor} no és un valor vàlid, un nivell correcte.")
        return valor_int
    except ValueError:
        raise argparse.ArgumentTypeError(f"{valor} no és un valor vàlid, ha de ser un valor enter")
    
def get_params():
    parser = argparse.ArgumentParser(description='Script amb arguments')
    parser.add_argument('--tiquets', type=valid_tikets_input, help='Nombre de tiquets que volem generar, màx: 100000')
    parser.add_argument('--max_products', type=valid_products_input, help='Nombre maxim de productes que poden haber-hi en un tiquet, màx: 50')
    parser.add_argument('--level', type=valid_lvl_input, help='Nivell de complexitat dels tiquets')
    
    args = parser.parse_args()
    
    numero_tiquets = args.tiquets
    max_products = args.max_products
    complexity_lvl = args.level

    return { 'numero_tiquets': numero_tiquets, 'max_products': max_products, 'complexity_lvl': complexity_lvl}

def random_num(n):
    return ''.join([str(np.random.randint(0,n+1)) for _ in range(n)])

def random_letter():
    letras = 'abcdefghijklmnopqrstuvwxyz'
    return np.random.choice(list(letras)).upper()

def get_current_date():
    now = datetime.now()
    return now.strftime("%d/%m/%Y")

def get_random_date(start_date='01/01/2000', end_date=None):
    if end_date is None:
        end_date = get_current_date()

    start_date = datetime.strptime(start_date, "%d/%m/%Y")
    end_date = datetime.strptime(end_date, "%d/%m/%Y")

    date_range = end_date - start_date

    random_seconds = random.randint(0, int(date_range.total_seconds()))

    random_date = start_date + timedelta(seconds=random_seconds)

    return random_date.strftime("%d/%m/%Y %H:%M")

def get_ticket_configuration(lvl_of_complexity_of_ticket, max_products):
    if lvl_of_complexity_of_ticket == 0:
        n_products = 5
        filtre = "format == 'ud'"

    elif lvl_of_complexity_of_ticket == 1:
        n_products = 5
        filtre = "format == 'kg'"

    elif lvl_of_complexity_of_ticket == 2:
        n_products = random.randint(1, max_products)
        filtre = "format == 'ud'"

    elif lvl_of_complexity_of_ticket == 3:
        n_products = random.randint(1, max_products)
        filtre = "format == 'kg'"

    elif lvl_of_complexity_of_ticket == 4:
        n_products = 5
        filtre = None

    else: # 5
        n_products = random.randint(1, max_products)
        filtre = None

    return {'n_products': n_products, 'filtre': filtre}

# Més informació de com convertir de coco a yolo: 
# https://medium.com/red-buffer/converting-a-custom-dataset-from-coco-format-to-yolo-format-6d98a4fd43fc
# O, al fitxer: products_object_detection.ipynb del repositori ocr-tiquets
def transform_coco_to_yolo(df, h, w, labels):
    df['etiqueta'] = df['etiqueta'].map(labels)

    df['element_width'] = df.apply(lambda row: (row.b_2[0] -row.b_1[0]), axis=1)
    df['element_height'] = df.apply(lambda row: (row.b_3[1] -row.b_1[1]), axis=1)

    df['element_width_norm'] = df.apply(lambda row: row.element_width /w, axis=1)
    df['element_height_norm'] = df.apply(lambda row: row.element_height /h, axis=1)

    df['x_center'] = df.apply(lambda row: (row.b_1[0] + (row.element_width /2)), axis=1)
    df['y_center'] = df.apply(lambda row: (row.b_1[1] + (row.element_height /2)), axis=1)

    df['x_center_norm'] = df.apply(lambda row: row.x_center /w, axis=1)
    df['y_center_norm'] = df.apply(lambda row: row.y_center /h, axis=1)

    return df

def save_yolo_format(df, container_height, ticket_width, labels, directory, ticket_id):
    df_yolo = transform_coco_to_yolo(df, container_height, ticket_width, labels)

    df_yolo = df_yolo[['etiqueta', 'x_center_norm', 'y_center_norm', 'element_width_norm', 'element_height_norm']]
    file_path = f'{directory}/{ticket_id}.txt'
    df_yolo.to_csv(file_path, sep=' ', index=False,  header=False)

__all__ = ['get_params', 'random_num', 'random_letter', 'get_random_date', 'get_ticket_configuration', 'transform_coco_to_yolo', 'save_yolo_format']

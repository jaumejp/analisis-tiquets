import pandas as pd
import numpy as np

import random
import jinja2
import base64
import os
import time
import shutil

import sys

from html2image import Html2Image
from PIL import Image

from utils.funcions import *
from utils.config import paths
from utils.variables import *

from clases.BlobGenerator import BlobGenerator

def read_csv(path):
    pass

if __name__ == "__main__":
    # Calculem el temps que tarda l'script
    inici = time.time()

    # Llegim els arguments que ens passen per terminal
    number_of_tickets_parameter, max_products_parameter, level_of_complexity = get_params().values()

    # level_of_complexity és un valor entre 0 i 5 que determina la complexitat del tiquet
    # Si es None, no hi ha parametre, borrar-ho tot i generarem totes les possibilitats
    # Si és un valor concret, només borrarem aquella complexitat

    # Parsegem els arguments i posem valors per defecte si no han passat parametres
    number_of_tikets = 1 if number_of_tickets_parameter is None else number_of_tickets_parameter
    max_products = 10 if max_products_parameter is None else max_products_parameter

    # Mostrem quants tiquets generarem:
    print(f"Generating {number_of_tikets} tiquets with {'all levels' if level_of_complexity is None else f'{level_of_complexity} level'} of complexity.")

    # Llegim el fitxer csv de productes per generar els tiquets amb productes aleatoris   
    df = pd.read_csv(paths['data']['products'], sep =",", dtype=dtype_dict)
    df['iva'] = df['iva'].astype(str)
    df['category_weight'] = df.category.apply(lambda x: escala_ponderacio[x])
    df = df.rename(columns={'price': 'p_u_sense_iva'})
    
    # Creem una llista amb els productes separats per dia.
    # Quan anem generant tiquets, només agafarem productes del mateix dia.
    dfs = [df.loc[df['ingested_day'] == date] for date in df.ingested_day.unique()]

    # Llegim els establiments per generar la informació del supermercat
    establishments = pd.read_csv(paths['data']['establishments'])
    establishments = establishments[establishments['provincia'].isin(cat)]
    
    # Creem un objecte ivas per calcular cada iva de cada tiquet
    # Més informació de com es genera a la documentació: generador-tiquets\generador_tiquets_documentacio.ipynb
    ivas = { iva: { 'd': int(iva) / 100, 'i': (int(iva) +100) / 100 } for iva in df.iva.unique() }

    # Carreguem la template en memòria
    # HTML
    template_directory = paths['template']['directory']
    template_name = paths['template']['file']
    template = jinja2.Environment(loader=jinja2.FileSystemLoader(template_directory), autoescape=jinja2.select_autoescape).get_template(template_name)

    # Imatges
    with open (paths['images']['logo_bottom'], "rb") as f:
        logo_bottom = base64.b64encode(f.read()).decode()

    with open (paths['images']['logo_contact_less'], "rb") as f:
        logo_contact_less = base64.b64encode(f.read()).decode()

    with open (paths['images']['logo_top'], "rb") as f:
        logo_top = base64.b64encode(f.read()).decode()

    # Objecte per convertir html a imatge (fa una captura de pantalla)
    # Dins el bucle, quan anem generant tiquets, farem servir aquest objecte per anar transformant els tiquets a imatge
    htmlimg = Html2Image()

    # Instància del generador de coordenades (en format coco).
    # Més informació de com es genera a la documentació: generador-tiquets\generador_tiquets_documentacio.ipynb
    ticket_generator_complete = BlobGenerator(initial_count=1, top_offset=290, ud=ud, kg=kg, total=total)
    ticket_generator_cropped = BlobGenerator(initial_count=0, top_offset=0, ud=ud_cropped, kg=kg_cropped, total=total_cropped)
    
    # Creem les carpetes per guardar els tiquets que exportarem. 
    # Si ja existeixen, ho borrem tot i tornem a crear-les
    current_directory = os.getcwd()

    # Directori on guardarem els tiquets:
    exported_data = os.path.join(current_directory, f"{paths['exports']['directory']}/data")

    if level_of_complexity is None:
        if os.path.exists(exported_data):
            # Borrar tot el que hi hagi a dins la carpeta data
            shutil.rmtree(exported_data)

            # Tornar a crear la carpeta data
            os.makedirs(exported_data)
        else:
            # Crear la carpeta data si no existeix
            os.makedirs(exported_data)

    else:
        # Borrar només la carpeta que tornarem a fer:
        level_of_complexity_directory = os.path.join(exported_data, f'complexity_{level_of_complexity}')
        if os.path.exists(level_of_complexity_directory):
            shutil.rmtree(level_of_complexity_directory)


    for level in range(6):
        # Creem tots els nivells de complexitat si no s'ha passat cap nivell de complexitat
            # level_of_complexity == None
        # Si s'ha passat un nivell de complexitat, només crearem aquell nivell (saltarem tots els altres)
            # level_of_complexity == 0 -> contuniue per: 1,2,3,4,5
        
        # Versió fàcil:
        # # # # # # if level_of_complexity is None or level == level_of_complexity:
        # # # # # #     # do code
        # # # # # # else:
        # # # # # #     continue
        
        if level_of_complexity is not None and level != level_of_complexity:
            continue

        # Per cada nivell de complexitat, creem una carpeta per guardar-hi els tiquets.
        # Descripció de cada nivell a: generador-tiquets\script\exported_data\descripció complexitats.txt
        directory_name = os.path.join(exported_data, f'complexity_{level}')
        os.makedirs(directory_name)

        # Dins de cada carpeta, creem les sub carpetes per guardar-hi les dades en format yolo i coco.
        # Creem totes les carpetes necessàries. (la estructura de carpetes també està a: generador-tiquets\script\exported_data\descripció complexitats.txt)
        
        # Carpetes per coco:
        coco_tickets = os.path.join(directory_name, 'coco', 'tickets')
        os.makedirs(coco_tickets)

        coco_tickets_cropped = os.path.join(directory_name, 'coco', 'cropped_area_products_in_ticket')
        os.makedirs(coco_tickets_cropped)

        # Carpetes per yolo:
        yolo_tickets = os.path.join(directory_name, 'yolo', 'tickets', 'images', 'train')
        os.makedirs(yolo_tickets)

        yolo_tickets_labels = os.path.join(directory_name, 'yolo', 'tickets', 'labels', 'train')
        os.makedirs(yolo_tickets_labels)
        
        yolo_tickets_cropped = os.path.join(directory_name, 'yolo', 'cropped_area_products_in_ticket', 'cuted_section', 'images', 'train')
        os.makedirs(yolo_tickets_cropped)

        cropped_area_products_in_ticket = os.path.join(directory_name, 'yolo', 'cropped_area_products_in_ticket', 'cuted_section', 'labels', 'train')
        os.makedirs(cropped_area_products_in_ticket)
        
        yolo_tickets_cropped_2 = os.path.join(directory_name, 'yolo', 'cropped_area_products_in_ticket', 'products_on_cuted_section', 'images', 'train')
        os.makedirs(yolo_tickets_cropped_2)
        
        products_on_cuted_section = os.path.join(directory_name, 'yolo', 'cropped_area_products_in_ticket', 'products_on_cuted_section', 'labels', 'train')
        os.makedirs(products_on_cuted_section)

        # Ara creem els fitxers per guardar-hi les dades en format yolo i coco. (fitxers == informació dels tiquets)

        # Creem uns dataframes buits per anar-hi concatenant les dades de cada tiquet
        df_bbx_products_in_ticket = pd.DataFrame()
        df_bbx_products_in_area = pd.DataFrame()
        df_bbx_area_products_in_ticket = pd.DataFrame()

        # Per cada nivell de complexitat, crearem diferents tiquets:
        for index_tiquet in range(1, number_of_tikets +1):
            tiket_name = f'{"{:06d}".format(index_tiquet)}'
            print()
            print("+++++ Generant Complexitat: ", level)
            print("+++++ Generant tiquet: ", tiket_name)

            # Calcular n productes per al tiquet i el filtre per agafar productes unitaris o per €/kg:
            n_products, filtre = get_ticket_configuration(level, max_products).values()
            rand_df_from_day = random.randint(0, len(dfs)-1)

            if filtre is not None:
                # Agafem un dia random entre tots els que hi hagi.
                # Agafem productes en base a uns pesos 'category_weight' que representa com de probable és que es compri un producte
                tiquet = dfs[rand_df_from_day].query(filtre).sample(n=n_products, weights='category_weight')
            else: 
                tiquet = dfs[rand_df_from_day].sample(n=n_products, weights='category_weight')

            # Un cop tenim els productes que hi hauran al tiquet. 

            # Tractem les dades perquè surtin bé a la plantilla:
            # Més informació de cada pas a: generador-tiquets\generador_tiquets_documentacio.ipynb
            tiquet['qty'] = tiquet.apply(lambda x: round(np.random.uniform(0.1, 1.5), 3) if x.format == 'kg' else np.random.choice([1, np.random.randint(2, 6)], p=[0.7, 0.3]), axis=1)
            tiquet['preu_sense_iva'] = (tiquet['p_u_sense_iva'] * tiquet['qty']).round(2)
            tiquet['preu_amb_iva'] = tiquet.apply(lambda x: ivas[x.iva]['i'] *x.preu_sense_iva, axis=1)
            tiquet['p_u_amb_iva'] = tiquet.apply(lambda x: x.p_u_sense_iva *ivas[x.iva]['i'], axis=1)
            
            ivas_list = []
            for iva in tiquet.iva.unique():
                total = (tiquet[tiquet['iva'] == iva]['preu_sense_iva'] *ivas[iva]['d']).sum()
                ivas_list.append({
                    "valor": f'{iva}%',
                    "base_imposable": total,
                    "quota": format(total *ivas[iva]['d'], ',.2f').replace(".", ",")
                })

            iva_total = sum([float(item['quota'].replace(',', '.')) for item in ivas_list])
            no_iva = format(sum([item['base_imposable'] for item in ivas_list]), ',.2f')

            for o in ivas_list:
                o['base_imposable'] = '{:.2f}'.format(float(o['base_imposable'])).replace('.', ',')

            total_amb_iva = format(tiquet['preu_amb_iva'].sum(), ',.2f').replace(".", ",")
            tiquet['preu_amb_iva'] = tiquet.preu_amb_iva.apply(lambda x: format(x, ',.2f').replace(".", ","))
            tiquet['p_u_amb_iva'] = tiquet.apply(lambda x: format(x.p_u_sense_iva *ivas[x.iva]['i'], ',.2f').replace(".", ","), axis=1)
            tiquet['qty'] = tiquet.apply(lambda x: format(x.qty, ',.0f') if x.format == 'ud' else x.qty, axis=1)

            # Creem un diccionari amb els productes per passar-ho a la plantilla i també per pasar-los al objecte BlobGenerator que determinarà les coordenades
            products = tiquet[['name', 'qty', 'p_u_amb_iva', 'preu_amb_iva', 'format']].rename(columns={
                'name': 'descripcio',
                'qty': 'quantitat',
                'p_u_amb_iva': 'preu_unitari',
                'preu_amb_iva': 'import',
            }).to_dict(orient='records')

            products = [{**p, 'quantitat_ud' if p['format'] == 'ud' else 'quantitat_kg': p['quantitat']} for p in products]
            products = [{k: v for k, v in p.items() if k != 'quantitat'} for p in products]

            tiquets_full = ticket_generator_complete.generate_blobs(products, tiket_name, total_amb_iva)
            ticket_generator_complete.increment_count(2)
            container_height = 290 + (ticket_generator_complete.count * 20) + 20 + 328 + 25

            # Creem dades random per la resta de informació de la plantilla
            rand_establishment = establishments.sample()

            rand_card = np.random.choice(cards, p=cards_weights/np.sum(cards_weights))
            targeta_1, targeta_2 = rand_card['targeta_1'], rand_card['targeta_2']

            # Creem el context per la plantilla
            context = {
                'nom': f"MERCADONA, S.A. {random_letter()}-{random_num(8)}",
                'adressa': rand_establishment.direccion.values[0],
                'ciutat': f"{rand_establishment.localidad.values[0]} {rand_establishment.codigo_postal.values[0]}",
                'telf': f"{rand_establishment.telefono.values[0]}",
                'data': f"{get_random_date()}",
                'op': f"{random_num(5)}",
                'factura_simplificada': f"{random_num(4)}-{random_num(3)}-{random_num(5)}",
                'rand_one_to_four': [np.random.randint(1, 5) for _ in range(60)],
                'products': products,
                'total_amb_IVA': total_amb_iva,
                'pagat_targeta_bancaria': total_amb_iva,
                'ivas': ivas_list,
                'total_sense_IVA': no_iva,
                'iva_total': format(iva_total, ',.2f').replace(".", ","),
                'targeta_bancaria': f"**** **** **** **** {random_num(4)}",
                'NC': random_num(9),
                'AUT': random_num(6),
                'AID': f"{random_letter()}00000000{random_num(5)}",
                'ARC': random_num(4),
                'targeta_1': targeta_1,
                'targeta_2': targeta_2,
                'total_amb_IVA': total_amb_iva,
                'logo_bottom': logo_bottom,
                'logo_top': logo_top,
                'logo_contact_less': logo_contact_less,
                'height': container_height,
            }

            reportText = template.render(context)

            # Guardem les imatges tant a la carpeta coco com yolo
            htmlimg.output_path = coco_tickets

            filesize = (500, container_height)

            htmlimg.screenshot(
                html_str=reportText,
                save_as=f'{tiket_name}.png',
                size=filesize
            )

            # Posem la imatge també a la carpeta yolo
            shutil.copy(f'{coco_tickets}/{tiket_name}.png', f'{yolo_tickets}/{tiket_name}.png')
            # També la guardem a la carpeta per identificar només la secció de productes: 
            shutil.copy(f'{coco_tickets}/{tiket_name}.png', f'{yolo_tickets_cropped}/{tiket_name}.png')

            # Creem la imatge tallada (crop de només on hi han els productes)
            b_1 = (25, 310)
            b_4 = (475, 270 + (ticket_generator_complete.count *20))

            pilImg = Image.open(f"{coco_tickets}/{tiket_name}.png")

            cropped_img = pilImg.crop((b_1[0], b_1[1], b_4[0], b_4[1]))
            cropped_img.save(f"{coco_tickets_cropped}/{tiket_name}.png")

            # Guardem la imatge també a la carpeta yolo. Si volem identificar els productes dins la secció
            shutil.copy(f'{coco_tickets_cropped}/{tiket_name}.png', f'{yolo_tickets_cropped_2}/{tiket_name}.png')

            # Calculem les coordenades dels productes si només tenim amb compte la secció. No el tiquet complert. com abans.
            tiquets_cropped = ticket_generator_cropped.generate_blobs(products, tiket_name, total_amb_iva)
            
            count = sum(1 if product['format'] == 'ud' else 2 for product in products) + 2

            products_area = {
                'ticket_id': tiket_name,
                'etiqueta': 'products',
                'value': None,
                'b_1': (25, 310),
                'b_2': (25 + 450, 310),
                'b_3': (25, (290 + (count * 20) +20)),
                'b_4': (25 + 450, (290 + (count * 20) +20)),
            }
            df_products_area = pd.DataFrame([products_area])

            # concatenar els dos dataframes amb el total
            df_bbx_products_in_ticket = pd.concat([df_bbx_products_in_ticket, tiquets_full], axis=0)
            df_bbx_products_in_area = pd.concat([df_bbx_products_in_area, tiquets_cropped], axis=0)
            df_bbx_area_products_in_ticket = pd.concat([df_bbx_area_products_in_ticket, df_products_area], axis=0)

            # Transforma de format coco a yolo i guardar els dataframes amb format .txt
            # Datasets de tot el tiquet amb els productes.
            ticket_width = 500
            labels = {'descripcio': 0, 'quantitat_ud': 1, 'quantitat_kg': 2, 'import': 3, 'total': 4, 'preu_unitari': 5}
            save_yolo_format(tiquets_full, container_height, ticket_width, labels, yolo_tickets_labels, tiket_name)
            
            # Dades dels productes dins la area de productes
            img_height = 290 + (count * 20) + 20 - 310
            img_width = 450
            labels = {'descripcio': 0, 'quantitat_ud': 1, 'quantitat_kg': 2, 'import': 3, 'total': 4, 'preu_unitari': 5}
            save_yolo_format(tiquets_cropped, img_height, img_width, labels, products_on_cuted_section, tiket_name)

            # Dades de només la secció de productes
            img_width = 500
            labels = {'products': 0}
            save_yolo_format(df_products_area, container_height, img_width, labels, cropped_area_products_in_ticket, tiket_name)
    
        # Guardar els dataframes coco
        coco_directory = os.path.join(directory_name, 'coco')

        df_bbx_products_in_ticket.to_csv(f'{coco_directory}/bbx_products_in_ticket.csv', index=False)
        df_bbx_products_in_area.to_csv(f'{coco_directory}/bbx_products_in_area.csv', index=False)
        df_bbx_area_products_in_ticket.to_csv(f'{coco_directory}/bbx_area_products_in_ticket.csv', index=False)


    # Mostrem el temps que tarda l'script en fer-ho tot
    fi = time.time()
    total = fi - inici
    print()
    print("Tiquets generats correctament.")
    h = int(total // 3600)
    m = int((total % 3600) // 60)
    s = int(total % 60)
    print()
    print("=====================================")
    print()
    print(f"Temps total: {h}h - {m}min - {s}seg")


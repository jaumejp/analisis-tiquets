from ultralytics import YOLO
import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment
from PIL import Image
import pytesseract

establishments = pd.read_csv("../../generador-tiquets/dades/establiments/establishments.csv")
establishments = establishments[establishments['provincia'].isin(['GIRONA', 'BARCELONA', 'LLEIDA', 'TARRAGONA'])]

tickets_template = {
    'nom': "MERCADONA, S.A. A-12345678",
    'adressa': 'C/ JOSEP MARÍA FOLCH I TORRES, 5',
    'ciutat': "TARRAGONA 43006",
    'telf': "977598991",
    'data': "22-04-2024",
    'op': "12345",
    'factura_simplificada': "1234-123-12345",
    'barcode': 'image',
    'total_amb_IVA': '', # total aquí
    'pagat_targeta_bancaria': '', # total aquí
    'total_sense_IVA': 'AAA,AA',
    'iva_total': '50,33',
    'targeta_bancaria': "**** **** **** **** 1234",
    'NC': '123456789',
    'AUT': '123456',
    'AID': "B0000000012345",
    'ARC': '1234',
    'targeta_1': 'VISA CREDITO/DEB',
    'targeta_2': 'Visa CaixaBank',
    'logo_bottom': 'image',
    'logo_top': 'image',
    'logo_contact_less': 'image',
    'products': [], # Productes aquí
    'ivas': [
        {
            'valor': '21%',
            'base_imposable':
            '44,01', 'quota':
            '9,24',
        },
        {
            'valor': '10%',
            'base_imposable': '3,48',
            'quota': '0,35'
        },
        {
            'valor': '4%',
            'base_imposable': '0,47',
            'quota': '0,02'
        }
    ]
}

def create_cost_matrix(Ytest, Ypred):
        cost_matrix = np.zeros((len(Ytest.values), len(Ypred.values)))

        for i, x in enumerate(Ytest.values):
            for j, y in enumerate(Ypred.values):
                cost_matrix[i, j] = abs(x - y)

        return cost_matrix

def get_relations(idxs_true, idxs_pred, Ytest, Ypred):
    relacions = {}

    for i in range(len(idxs_true)):
        idx_descripcio = Ytest[Ytest == Ytest.values[idxs_true[i]]].index[0]
        idx_label = Ypred[Ypred == Ypred.values[idxs_pred[i]]].index[0]

        relacions[idx_descripcio] = idx_label

    return relacions

def get_rand_establishment():
    return establishments.sample()

def get_text(row, pilImg):
    cropped_img = pilImg.crop((row.b_1[0], row.b_1[1], row.b_4[0], row.b_4[1]))

    img = np.array(cropped_img)
    text = pytesseract.image_to_string(img, config="--psm 7")

    return text

def relate_bbox(inference, image):
    data = []

    data_boxes = inference[0].boxes.data

    data_boxes_np = data_boxes.cpu().detach().numpy()

    for bbx in data_boxes_np.tolist():
        data.append({
        'x1': bbx[0],
        'y1': bbx[1],
        'x2': bbx[2],
        'y2': bbx[3],
        'acc': bbx[4],
        'label': bbx[5]
        })

    predicts = pd.DataFrame(data)

    predicts['label_name'] = predicts['label'].map(inference[0].names)

    predicts['b_1'] = predicts.apply(lambda row: (row.x1, row.y1), axis = 1)
    predicts['b_4'] = predicts.apply(lambda row: (row.x2, row.y2), axis = 1)


    pilImg = Image.open(image)

    predicts['value'] = predicts.apply(lambda row : get_text(row, pilImg), axis = 1)

    ticket_info = {'ticket_id': {}}

    g_df = predicts[predicts['label_name'] != 'total'].copy()

    Ytest = g_df[g_df['label_name'] == 'descripcio'].y1

    for label in ['import', 'quantitat_ud', 'quantitat_kg']:
        Ypred = g_df[g_df['label_name'] == label].y1

        if label == 'quantitat_kg':
            Ypred -= 20

        cost_matrix = create_cost_matrix(Ytest, Ypred)

        idxs_true, idxs_pred = linear_sum_assignment(cost_matrix)

        for i in range(len(idxs_true)):
            idx_descripcio = Ytest[Ytest == Ytest.values[idxs_true[i]]].index[0] #[0] perquè retornaba un objecte Index

            # Crear el atribut descripcio_id (que és el id d'aquesta descripció)
            if idx_descripcio not in ticket_info['ticket_id']:
                ticket_info['ticket_id'][idx_descripcio] = {}

            idx_label = Ypred[Ypred == Ypred.values[idxs_pred[i]]].index[0]

            ticket_info['ticket_id'][idx_descripcio][label] = idx_label



    # preu unitari dels kg
    Ytest = g_df[g_df['label_name'] == 'quantitat_kg'].y1
    Ypred = g_df[g_df['label_name'] == 'preu_unitari'].y1

    cost_matrix = create_cost_matrix(Ytest, Ypred)
    idxs_true, idxs_pred = linear_sum_assignment(cost_matrix)

    relacions = get_relations(idxs_true, idxs_pred, Ytest, Ypred)


    # Això està fora i he tallat el bucle i l'he tornat a començar perquè sinó no em deixava
    # modificar l'objecte ticket_info, donava error : RuntimeError: dictionary changed size during iteration
    copied_items = dict(ticket_info['ticket_id']).copy()

    for k_1, v_1 in relacions.items():
        # Busquem a quina descripció (key del diccionari interior de ticket_info['00000X])
        # Té a dins
        for k_2, v_2 in copied_items.items():
            x = v_2.copy()
            for v_3 in x.values(): # Aquí donava el error
                if v_3 == k_1:
                    ticket_info['ticket_id'][k_2]['preu_unitari'] = v_1.copy()

    # preu unitari dels ud
    preus_unitaris = g_df[g_df['label_name'] == 'preu_unitari'].y1
    preus_unitaris_ud = preus_unitaris.drop(relacions.values())

    Ytest = g_df[g_df['label_name'] == 'descripcio'].y1
    Ypred = preus_unitaris_ud

    cost_matrix = create_cost_matrix(Ytest, Ypred)
    idxs_true, idxs_pred = linear_sum_assignment(cost_matrix)

    for i in range(len(idxs_true)):
        idx_descripcio = Ytest[Ytest == Ytest.values[idxs_true[i]]].index[0] #[0] perquè retornaba un objecte Index

        # Crear el atribut descripcio_id (que és el id d'aquesta descripció)
        if idx_descripcio not in ticket_info['ticket_id']:
            ticket_info['ticket_id'][idx_descripcio] = {}

        idx_label = Ypred[Ypred == Ypred.values[idxs_pred[i]]].index[0]

        ticket_info['ticket_id'][idx_descripcio]['preu_unitari'] = idx_label

    data = []

    tiquet_obj = ticket_info['ticket_id']

    for key, value in tiquet_obj.items():
        descripcio_id = key
        quantitat_ud_id = value.get('quantitat_ud', None)
        quantitat_kg_id = value.get('quantitat_kg', None)
        preu_unitari_id = value.get('preu_unitari', None)
        import_id = value.get('import', None)

        if quantitat_ud_id is not None:
            quantitat = predicts.iloc[quantitat_ud_id].value
        elif quantitat_kg_id is not None:
            quantitat = predicts.iloc[quantitat_kg_id].value
        else:
            quantitat = '1'
        
        if preu_unitari_id is not None:
            preu_unitari = predicts.iloc[preu_unitari_id].value
        elif import_id is not None: 
            preu_unitari = predicts.iloc[import_id].value
        else:
            preu_unitari = '1'

        if import_id is not None:
            _import = predicts.iloc[import_id].value
        else:
            _import = 'no detection'

        data.append({
            'descripcio': predicts.iloc[descripcio_id].value,
            'quantitat': quantitat,
            'preu_unitari': preu_unitari,
            'import': _import
        })

    total_row = predicts[predicts['label_name'] == 'total']

    # Update products and total
    tickets_template['products'] = data
    tickets_template['total_amb_IVA'] = total_row.value.values[0]
    tickets_template['pagat_targeta_bancaria'] = total_row.value.values[0]  

    # Add random establishment
    rand_establishment = get_rand_establishment()
    tickets_template['ciutat'] = f"{rand_establishment.localidad.values[0]} {rand_establishment.codigo_postal.values[0]}"
    
    return tickets_template


__all__ = ['relate_bbox']
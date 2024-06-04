import pandas as pd

class BlobGenerator:
    def __init__(self, initial_count, top_offset, ud, kg, total):
        self.count = initial_count
        self.initial_count = initial_count
        self.top_offset = top_offset
        self.ud = ud
        self.kg = kg
        self.total = total
        self.item_height = 20
        self.tiquets = None
    
    def _reset_count(self):
        self.count = self.initial_count

    def _coords(self, format_dict,count, key):
        left = format_dict[key]['left']
        top = self.top_offset + (count *self.item_height)
        width = format_dict[key]['width']

        return {
            '1': (left, top),
            '2': (left + width, top),
            '3': (left, top + self.item_height),
            '4': (left + width, top + self.item_height),
        }

    def generate_blobs(self, products, ticket_num, total_amb_iva):
        self._reset_count()

        tiquets = []
        for product in products:
            if product['format'] == 'ud':
                for key in self.ud.keys():
                    
                    # Si només tenim 1 unitat, no posem preu unitari, per tant no necessitem blob d'aquell espai
                    if key == 'preu_unitari' and product['quantitat_ud'] == '1': continue
                        
                    tiquets.append({
                        'ticket_id': f'{ticket_num}',
                        'etiqueta': key,
                        'value': product[key],
                        'blob': self._coords(self.ud, self.count, key),
                    })
                self.count = self.count + 1
            else:
                for key in self.kg.keys():
                    tiquets.append({
                        'ticket_id': f'{ticket_num}',
                        'etiqueta': key,
                        'value': product[key],
                        'blob': self._coords(self.kg, self.count if key == 'descripcio' else self.count +1, key),
                    })
                self.count = self.count + 2

        # Blank row
        self.count += 1
        tiquets.append({
            'ticket_id': f'{ticket_num}',
            'etiqueta': 'total',
            'value':  total_amb_iva,
            'blob': self._coords(self.total, self.count, 'total'),
        })
        
        # Tractem l'array de tiquets per passar-lo a dataframe i convertir-lo correctament
        self.tiquets = pd.DataFrame(tiquets)
        self.tiquets[['b_1', 'b_2', 'b_3', 'b_4']] = self.tiquets.blob.apply(lambda b: pd.Series([b['1'], b['2'], b['3'], b['4']]))
        self.tiquets.drop('blob', axis=1, inplace=True)
        return self.tiquets

    def increment_count(self, n):
        self.count += n

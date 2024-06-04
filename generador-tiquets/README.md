# Generador de tiquets

En el cas de que es vulguin exportar els tiquets en una ubicació diferent, s'ha de configurar el fitxer `config.py`. 

#### Executar el programa
```python
python main.py --tiquets 10 --max_products 5 --level 5
```
- `--tiquets`: Quants tiquets volem generar. Màxim: 100000, si no especifiquem en farà 1.
- `--max_products`: Quants productes volem com a màxim al tiquet entre (1, n). Màxim 10, si no especifiquem en farà 10.
- `--level`: De quina forma volem crear el dataset. Més informació dels nivells a la memòria.


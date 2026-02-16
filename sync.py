
"""
Script de sincronización desde Google Sheets CSV a data/productos.json
Requiere: pip install requests
"""
import csv, json, requests
CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQa1ChnXD62p6wdOHyDQMEtP8q311HY4x8W4kaUyxHIqrM4KobaSrxVYQbU07c-K8WWaZJ746BwuKDh/pub?output=csv'  # reemplazar
OUT_PATH = 'data/productos.json'


def parse_currency_to_number(s: str) -> float:
    if s is None:
        return 0.0

    # Quitar moneda, espacios, letras
    t = ''.join(ch for ch in s if ch.isdigit() or ch in ',.-')

    has_comma = ',' in t
    has_dot = '.' in t

    # Si tiene ambos separadores, decide por el último como decimal
    if has_comma and has_dot:
        last_comma = t.rfind(',')
        last_dot = t.rfind('.')
        if last_dot > last_comma:
            # último es '.', decimal = '.', miles = ','
            t = t.replace(',', '')
            # deja el '.', ejemplo: "45,200.00" -> "45200.00"
        else:
            # último es ',', decimal = ',', miles = '.'
            t = t.replace('.', '')    # "1.234,56" -> "1234,56"
            t = t.replace(',', '.')   # "1234,56"  -> "1234.56"
    elif has_comma and not has_dot:
        # sólo coma: coma decimal
        t = t.replace('.', '')
        t = t.replace(',', '.')
    elif has_dot and not has_comma:
        # sólo punto: punto decimal
        t = t.replace(',', '')

    try:
        return float(t)
    except:
        return 0.0


def sync():
    r = requests.get(CSV_URL, timeout=20)
    r.raise_for_status()
    text = r.text.splitlines()
    reader = csv.DictReader(text)
    out = []
    for row in reader:
        codigo = (row.get('Codigo') or '').strip()
        nombre = (row.get('Nombre') or '').strip()
        precio_str = (row.get('Precio') or '').strip()
        if codigo and nombre:
            out.append({
                'Codigo': codigo,
                'Nombre': nombre,
                'Precio': parse_currency_to_number(precio_str)
            })
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    sync()
    print(f'Sincronizado {OUT_PATH}')

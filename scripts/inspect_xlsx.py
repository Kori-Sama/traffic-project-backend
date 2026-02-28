import os
import zipfile
import xml.etree.ElementTree as ET
import sys

def parse_xlsx_raw(f):
    """Simple XLSX parser using zip and xml to avoid openpyxl dependency."""
    with zipfile.ZipFile(f) as z:
        strings = []
        try:
            with z.open('xl/sharedStrings.xml') as f_str:
                tree_str = ET.parse(f_str)
                # Correctly find all text nodes in sharedStrings.xml
                strings = [t.text for t in tree_str.getroot().findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')]
        except Exception as e:
            print(f"Error reading shared strings: {e}")
            pass
        
        with z.open('xl/worksheets/sheet1.xml') as f_xml:
            tree = ET.parse(f_xml)
            root = tree.getroot()
            rows = []
            for row in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                cells = {}
                for cell in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    r = cell.get('r') # e.g., 'A1'
                    col = ''.join([c for c in r if not c.isdigit()])
                    t = cell.get('t')
                    v_node = cell.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    if v_node is not None:
                        val = v_node.text
                        if t == 's':
                            try:
                                val = strings[int(val)] if int(val) < len(strings) else val
                            except (ValueError, IndexError):
                                pass
                        cells[col] = val
                if cells:
                    rows.append(cells)
            return rows

rows = parse_xlsx_raw('data/隆纳路段门架经纬度明细表.xlsx')
for row in rows[:10]:
    print(row)

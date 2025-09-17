#!/usr/bin/env python3
"""
Medžio struktūros analizės programa.
Nuskaito CSV failą su medžio duomenimis ir išveda ASCII lentelę su atšakų skaičiumi.
"""

import argparse
import csv
import sys
from typing import List, Dict, Any, Optional


class TreeAnalyzer:
    """Klasė medžio struktūros analizei ir atvaizdavimui."""
    
    def __init__(self, data: List[Dict[str, Any]], hierarchy_columns: List[str]):
        self.data = data
        self.hierarchy_columns = hierarchy_columns
        self.all_columns = list(data[0].keys()) if data else []
        
    def analyze_tree_structure(self) -> List[Dict[str, Any]]:
        """
        Analizuoja medžio struktūrą ir suskaičiuoja atšakų skaičių.
        
        Returns:
            List[Dict]: Duomenys su pridėtu 'nodes' stulpeliu
        """
        result_data = []
        
        for i, row in enumerate(self.data):
            new_row = row.copy()
            
            # Randame hierarchijos lygmenį šiai eilutei
            hierarchy_level = self._find_hierarchy_level(row)
            
            # Skaičiuojame atšakas tik jei tai ne viršūnė (ne paskutinis lygmuo)
            if hierarchy_level is not None and hierarchy_level < len(self.hierarchy_columns) - 1:
                nodes_count = self._count_child_nodes(i, hierarchy_level)
                new_row['nodes'] = nodes_count
            else:
                new_row['nodes'] = ''
                
            result_data.append(new_row)
            
        return result_data
    
    def _find_hierarchy_level(self, row: Dict[str, Any]) -> Optional[int]:
        """
        Nustato, kuriame hierarchijos lygyje yra eilutė.
        
        Args:
            row: Duomenų eilutė
            
        Returns:
            int: Hierarchijos lygmens indeksas arba None
        """
        for i, col in enumerate(self.hierarchy_columns):
            if row.get(col) and str(row[col]).strip():
                return i
        return None
    
    def _count_child_nodes(self, parent_index: int, parent_level: int) -> int:
        """
        Suskaičiuoja tiesioginių atšakų skaičių duotam mazgui.
        
        Args:
            parent_index: Tėvinio mazgo indeksas duomenyse
            parent_level: Tėvinio mazgo hierarchijos lygmuo
            
        Returns:
            int: Atšakų skaičius
        """
        parent_row = self.data[parent_index]
        child_level = parent_level + 1
        
        if child_level >= len(self.hierarchy_columns):
            return 0
            
        child_column = self.hierarchy_columns[child_level]
        count = 0
        
        # Ieškome atšakų po tėvinio mazgo
        for i in range(parent_index + 1, len(self.data)):
            row = self.data[i]
            
            # Jei randame naują mazgą tėvinio lygio ar aukštesnio - stabdome paiešką
            current_level = self._find_hierarchy_level(row)
            if current_level is not None and current_level <= parent_level:
                break
                
            # Jei randame tiesioginę atšaką
            if (current_level == child_level and 
                row.get(child_column) and 
                str(row[child_column]).strip()):
                
                # Patikriname, ar tai tikrai šio tėvo atšaka
                if self._is_child_of_parent(row, parent_row, parent_level):
                    count += 1
                    
        return count
    
    def _is_child_of_parent(self, child_row: Dict[str, Any], 
                           parent_row: Dict[str, Any], 
                           parent_level: int) -> bool:
        """
        Patikrina, ar duotas mazgas yra konkretaus tėvo atšaka.
        
        Args:
            child_row: Galimos atšakos eilutė
            parent_row: Tėvinio mazgo eilutė
            parent_level: Tėvinio mazgo lygmuo
            
        Returns:
            bool: True, jei tai tiesioginis vaikas
        """
        # Tikriname visus aukštesnius hierarchijos lygmenis
        for level in range(parent_level + 1):
            parent_col = self.hierarchy_columns[level]
            parent_val = parent_row.get(parent_col, '')
            child_val = child_row.get(parent_col, '')
            
            if level == parent_level:
                # Šiame lygyje tėvas turi turėti reikšmę, o vaikas - ne
                if not (parent_val and str(parent_val).strip() and 
                       not (child_val and str(child_val).strip())):
                    return False
            else:
                # Aukštesniuose lygiuose reikšmės turi sutapti
                if str(parent_val).strip() != str(child_val).strip():
                    return False
                    
        return True


class TableFormatter:
    """Klasė ASCII lentelės formatavimui."""
    
    @staticmethod
    def format_table(data: List[Dict[str, Any]], columns: List[str]) -> str:
        """
        Formuoja ASCII lentelę.
        
        Args:
            data: Duomenų sąrašas
            columns: Stulpelių sąrašas
            
        Returns:
            str: Suformatuota ASCII lentelė
        """
        if not data:
            return ""
            
        # Skaičiuojame stulpelių plotius
        col_widths = {}
        for col in columns:
            col_widths[col] = len(col)
            for row in data:
                value = str(row.get(col, '')).strip()
                col_widths[col] = max(col_widths[col], len(value))
        
        # Formuojame antraštę
        header_parts = []
        for col in columns:
            header_parts.append(col.ljust(col_widths[col]))
        header = " | ".join(header_parts)
        
        # Formuojame duomenų eilutes
        rows = [header]
        for row in data:
            row_parts = []
            for col in columns:
                value = str(row.get(col, '')).strip()
                row_parts.append(value.ljust(col_widths[col]))
            rows.append(" | ".join(row_parts))
            
        return "\n".join(rows)


def read_csv_file(filename: str) -> List[Dict[str, Any]]:
    """
    Nuskaito CSV failą ir grąžina duomenų sąrašą.
    
    Args:
        filename: Failo pavadinimas
        
    Returns:
        List[Dict]: Nuskaitytų duomenų sąrašas
    """
    try:
        with open(filename, 'r', encoding='utf-8', newline='') as file:
            # Bandome nustatyti delimitatorių
            sample = file.read(1024)
            file.seek(0)
            
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(file, delimiter=delimiter)
            data = []
            
            for row in reader:
                # Pašaliname tarpus iš raktų
                cleaned_row = {key.strip(): value for key, value in row.items()}
                data.append(cleaned_row)
                
            return data
            
    except FileNotFoundError:
        print(f"Klaida: failas '{filename}' nerastas.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Klaida skaitant failą: {e}", file=sys.stderr)
        sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """Apdoroja komandinės eilutės argumentus."""
    parser = argparse.ArgumentParser(
        description='Analizuoja medžio struktūrą CSV faile ir prideda atšakų skaičių.'
    )
    
    parser.add_argument(
        'filename',
        help='CSV failo pavadinimas'
    )
    
    parser.add_argument(
        '-d',
        '--depth',
        required=True,
        help='Hierarchijos stulpeliai, atskirti kableliais (pvz., database,table,column)'
    )
    
    return parser.parse_args()


def main():
    """Pagrindinė programos funkcija."""
    args = parse_arguments()
    
    # Nuskaitome duomenis
    data = read_csv_file(args.filename)
    
    if not data:
        print("Klaida: failas tuščias arba neturi duomenų.", file=sys.stderr)
        sys.exit(1)
    
    # Apdorojame hierarchijos stulpelius
    hierarchy_columns = [col.strip() for col in args.depth.split(',')]
    
    # Patikriname, ar visi nurodyti stulpeliai egzistuoja
    available_columns = list(data[0].keys())
    missing_columns = [col for col in hierarchy_columns if col not in available_columns]
    
    if missing_columns:
        print(f"Klaida: stulpeliai neegzistuoja: {', '.join(missing_columns)}", file=sys.stderr)
        print(f"Galimi stulpeliai: {', '.join(available_columns)}", file=sys.stderr)
        sys.exit(1)
    
    # Analizuojame medžio struktūrą
    analyzer = TreeAnalyzer(data, hierarchy_columns)
    result_data = analyzer.analyze_tree_structure()
    
    # Formuojame išvesties stulpelius
    output_columns = available_columns + ['nodes']
    
    # Išvedame lentelę
    formatter = TableFormatter()
    table = formatter.format_table(result_data, output_columns)
    print(table)


if __name__ == '__main__':
    main()
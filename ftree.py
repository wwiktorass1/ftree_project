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
    def __init__(self, data: List[Dict[str, Any]], hierarchy_columns: List[str]):
        self.data = data
        self.hierarchy_columns = hierarchy_columns
        self.all_columns = list(data[0].keys()) if data else []
        
    def analyze_tree_structure(self) -> List[Dict[str, Any]]:
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
        for i, col in enumerate(self.hierarchy_columns):
            if row.get(col) and str(row[col]).strip():
                return i
        return None
    
    def _count_child_nodes(self, parent_index: int, parent_level: int) -> int:
        parent_row = self.data[parent_index]
        child_level = parent_level + 1
        
        if child_level >= len(self.hierarchy_columns):
            return 0
            
        child_column = self.hierarchy_columns[child_level]
        count = 0
        
        for i in range(parent_index + 1, len(self.data)):
            row = self.data[i]
            
            current_level = self._find_hierarchy_level(row)
            if current_level is not None and current_level <= parent_level:
                break
                
            if (current_level == child_level and 
                row.get(child_column) and 
                str(row[child_column]).strip()):
                
                if self._is_child_of_parent(row, parent_row, parent_level):
                    count += 1
                    
        return count
    
    def _is_child_of_parent(self, child_row: Dict[str, Any], 
                           parent_row: Dict[str, Any], 
                           parent_level: int) -> bool:
        """
        Patikrina, ar child_row yra tiesioginis parent_row vaikas.
        """
        for level in range(parent_level + 1):
            parent_col = self.hierarchy_columns[level]
            parent_val = str(parent_row.get(parent_col, '')).strip()
            child_val = str(child_row.get(parent_col, '')).strip()
            
            if level == parent_level:
                # Tėvas turi reikšmę, o vaikas šiame lygyje – tuščią
                if not (parent_val and not child_val):
                    return False
            else:
                # Aukštesniuose lygiuose reikšmės turi sutapti
                if child_val not in (parent_val, ""):
                    return False
                    
        return True


class TableFormatter:
    """Klasė ASCII lentelės formatavimui."""
    
    @staticmethod
    def format_table(data: List[Dict[str, Any]], columns: List[str]) -> str:
        if not data:
            return ""
            
        col_widths = {}
        for col in columns:
            col_widths[col] = len(col)
            for row in data:
                value = str(row.get(col, '')).strip()
                col_widths[col] = max(col_widths[col], len(value))
        
        # Antraštė
        header_parts = []
        for col in columns:
            header_parts.append(col.ljust(col_widths[col]))
        header = " | ".join(header_parts)
        
        # Eilutės
        rows = [header]
        for row in data:
            row_parts = []
            for col in columns:
                value = str(row.get(col, '')).strip()
                row_parts.append(value.ljust(col_widths[col]))
            rows.append(" | ".join(row_parts))
            
        return "\n".join(rows)


def read_csv_file(filename: str) -> List[Dict[str, Any]]:
    try:
        with open(filename, 'r', encoding='utf-8', newline='') as file:
            sample = file.read(1024)
            file.seek(0)
            
            # Bandome automatiškai nustatyti delimiter
            delimiter = ','  # Default delimiter
            
            try:
                sniffer = csv.Sniffer()
                detected_delimiter = sniffer.sniff(sample).delimiter
                delimiter = detected_delimiter
            except csv.Error:
                # Jei sniffer neveikia, bandome įprastus delimiter'ius
                possible_delimiters = [',', ';', '\t', '|']
                max_columns = 0
                best_delimiter = ','
                
                for test_delimiter in possible_delimiters:
                    file.seek(0)
                    test_reader = csv.reader(file, delimiter=test_delimiter)
                    try:
                        first_row = next(test_reader)
                        if len(first_row) > max_columns:
                            max_columns = len(first_row)
                            best_delimiter = test_delimiter
                    except (StopIteration, csv.Error):
                        continue
                
                delimiter = best_delimiter
                print(f"Naudojamas delimiter: '{delimiter}'", file=sys.stderr)
            
            file.seek(0)
            reader = csv.DictReader(file, delimiter=delimiter)
            data = []
            
            for row in reader:
                cleaned_row = {}
                for key, value in row.items():
                    if key is not None:
                        cleaned_key = key.strip()
                        cleaned_value = value.strip() if value is not None else ''
                        cleaned_row[cleaned_key] = cleaned_value
                data.append(cleaned_row)
                
            return data
            
    except FileNotFoundError:
        print(f"Klaida: failas '{filename}' nerastas.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Klaida skaitant failą: {e}", file=sys.stderr)
        sys.exit(1)


def parse_arguments() -> argparse.Namespace:
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
    args = parse_arguments()
    
    data = read_csv_file(args.filename)
    
    if not data:
        print("Klaida: failas tuščias arba neturi duomenų.", file=sys.stderr)
        sys.exit(1)
    
    hierarchy_columns = [col.strip() for col in args.depth.split(',')]
    
    available_columns = list(data[0].keys())
    missing_columns = [col for col in hierarchy_columns if col not in available_columns]
    
    if missing_columns:
        print(f"Klaida: stulpeliai neegzistuoja: {', '.join(missing_columns)}", file=sys.stderr)
        print(f"Galimi stulpeliai: {', '.join(available_columns)}", file=sys.stderr)
        sys.exit(1)
    
    analyzer = TreeAnalyzer(data, hierarchy_columns)
    result_data = analyzer.analyze_tree_structure()
    
    output_columns = available_columns + ['nodes']
    
    formatter = TableFormatter()
    table = formatter.format_table(result_data, output_columns)
    print(table)


if __name__ == '__main__':
    main()

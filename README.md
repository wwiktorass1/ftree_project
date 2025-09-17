# ftree – CSV Tree Analyzer

Ši programa analizuoja CSV faile pateiktą medžio struktūrą ir ASCII lentelės pavidalu išveda rezultatą su papildomu stulpeliu **nodes**, kuriame pateikiamas kiekvieno mazgo atšakų (vaikų) skaičius. Viršūnės (lapai) neturi nodes reikšmės.

---

## 🚀 Paleidimas

### Reikalavimai
- Python 3.8+
- Standartinė biblioteka (nereikia papildomų paketų)

### Naudojimas

```bash
python ftree.py <csv_failas> -d <stulpeliai>
```

- `<csv_failas>` – kelias iki CSV failo
- `-d <stulpeliai>` – hierarchijos stulpeliai, atskirti kableliais (pvz. `database,table,column`)

---

## 📂 Pavyzdžiai

### Pavyzdys 1

**Įvestis:** `data/data1.csv`
```csv
database,table,column,type,title
DB,,,,Database name
,TBL,,Table name,
,,COL1,integer,Column 1
,,COL2,string,Column 2
```

**Komanda:**
```bash
python ftree.py data/data1.csv -d database,table,column
```

**Rezultatas:**
```
database | table | column | type    | title         | nodes
DB       |       |        |         | Database name | 1
         | TBL   |        | Table name |            | 2
         |       | COL1   | integer | Column 1      | 
         |       | COL2   | string  | Column 2      | 
```

---

### Pavyzdys 2

**Įvestis:** `data/data2.csv`
```csv
a,b,c
1,,i
,1.1,x
,1.2,y
2,,j
,2.1,z
```

**Komanda:**
```bash
python ftree.py data/data2.csv -d a,b
```

**Rezultatas:**
```
a | b   | c  | nodes
1 |     | i  | 2
  | 1.1 | x  | 
  | 1.2 | y  | 
2 |     | j  | 1
  | 2.1 | z  | 
```

---

## ⚙️ Struktūra
- `ftree.py` – pagrindinis programos failas
- `data/` – pavyzdiniai CSV failai

---

## 📌 Pastabos
- Programa veikia be papildomų bibliotekų.
- Jei CSV failas neteisingas (nėra nurodytų stulpelių), gausite klaidos pranešimą.
- Papildomi testai gali būti pridėti su `pytest`.

---

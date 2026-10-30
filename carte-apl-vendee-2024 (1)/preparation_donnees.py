#!/usr/bin/env python3
"""Prépare le fichier statique à partir du XLSX DREES et de l'API publique Géo."""
import argparse, json, re, sys, pathlib
from openpyxl import load_workbook
from shapely.geometry import shape
from shapely.strtree import STRtree
import requests
ROOT=pathlib.Path(__file__).resolve().parent
URL='https://geo.api.gouv.fr/departements/85/communes?fields=nom,code&format=geojson&geometry=contour'
def code(s):
    if s is None:return None
    v=str(s).strip()
    if re.fullmatch(r'85\d{3}(?:\.0)?',v):return v[:5]
    return None
def number(v):
    if isinstance(v,(float,int)) and not isinstance(v,bool):return float(v)
    if isinstance(v,str):
        try:return float(v.strip().replace(' ','').replace(',','.'))
        except ValueError:pass
    return None
def extract_xlsx(path):
    wb=load_workbook(path,read_only=True,data_only=True)
    names=[s for s in wb.sheetnames if '2024' in s]
    if not names:raise ValueError('Aucune feuille contenant 2024 dans le classeur. Feuilles : '+', '.join(wb.sheetnames))
    sheet=wb[names[0]]; values={}; duplicates=[]
    # Structure du fichier DREES : colonne A = code INSEE, colonne C = APL généralistes de tous âges.
    for row in sheet.iter_rows(values_only=True):
        if len(row)<3:continue
        c=code(row[0]);v=number(row[2]);
        if c:
            if c in values:duplicates.append(c)
            values[c]=v
    if duplicates:raise ValueError('Doublons de codes INSEE : '+', '.join(sorted(set(duplicates))))
    if len(values)<200:raise ValueError(f'Seulement {len(values)} communes vendéennes trouvées : vérifiez les colonnes et la feuille du classeur.')
    return values,names[0]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--xlsx',required=True,help='Classeur officiel DREES de généralistes');ap.add_argument('--geojson',help='Fichier de contours local si l’API n’est pas accessible');ap.add_argument('--national',type=float,help='Valeur nationale vérifiée, facultative');args=ap.parse_args()
    vals,sheet=extract_xlsx(args.xlsx)
    if args.geojson:geo=json.loads(pathlib.Path(args.geojson).read_text(encoding='utf8'))
    else:
        resp=requests.get(URL,timeout=70);resp.raise_for_status();geo=resp.json()
    feats=geo['features'] if isinstance(geo,dict) and geo.get('type')=='FeatureCollection' else geo
    out=[];seen=set()
    for f in feats:
        p=f.get('properties') or {};c=str(p.get('code') or p.get('INSEE_COM') or '')
        if not c.startswith('85') or len(c)!=5:continue
        if c in seen:raise ValueError('Code INSEE dupliqué dans les contours : '+c)
        seen.add(c);v=vals.get(c)
        out.append({'type':'Feature','geometry':f['geometry'],'properties':{'code':c,'nom':p.get('nom') or p.get('NOM') or c,'apl':round(v,5) if v is not None else None,'voisins':[]}})
    if len(out)<200:raise ValueError('Contours insuffisants : '+str(len(out)))
    # Limite communale partagée : contacts le long d'une ligne, pas juste au point triple.
    geoms=[shape(f['geometry']) for f in out];tree=STRtree(geoms)
    for i,g in enumerate(geoms):
        for ix in tree.query(g):
            j=int(ix)
            if j<=i:continue
            h=geoms[j]
            if g.boundary.intersection(h.boundary).length>0.00001:
                out[i]['properties']['voisins'].append(out[j]['properties']['code'])
                out[j]['properties']['voisins'].append(out[i]['properties']['code'])
    missing=sorted(seen-set(vals));old=sorted(set(vals)-seen)
    result={'type':'FeatureCollection','metadata':{'source':'DREES APL généralistes 2024','feuille':sheet,'contours':'API Géo communes, consultée lors de la préparation','moyenne_nationale':args.national,'communes_manquantes':missing,'codes_apl_sans_contour':old,'note':'Référence nationale non affichée si elle n’a pas été vérifiée et renseignée.'},'features':out}
    dest=ROOT/'donnees-vendee.json';dest.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf8')
    print(f'{len(out)} contours; {sum(f["properties"]["apl"] is not None for f in out)} APL renseignés; {len(missing)} manquants; {len(old)} anciens codes ou discordants')
    if missing:print('Sans APL :',', '.join(missing))
    if old:print('APL sans contour actuel :',', '.join(old))
    print('Fichier créé :',dest)
if __name__=='__main__':
    try:main()
    except Exception as e:sys.exit('ERREUR : '+str(e))

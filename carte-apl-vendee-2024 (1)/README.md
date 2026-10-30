# Alouette — carte interactive APL des généralistes en Vendée

**État : 253 valeurs APL 2024 officielles intégrées (253 codes INSEE distincts, aucun APL absent).** La moyenne nationale de 3,72165 a été calculée par moyenne des valeurs de la colonne C pondérées par la population standardisée de la colonne G, sur 34 890 communes du fichier France hors Mayotte. Le résultat s’affiche arrondi à 3,72. **Contours non inclus localement : la page récupère les frontières officielles auprès de l'API Géo lors de son chargement dans le navigateur.** Si ce service est indisponible ou refuse la requête, la carte affichera une erreur. Ce point n'a pas pu être testé de bout en bout dans l'environnement de création ; vérifiez impérativement avant publication éditoriale.

L’extraction est effectuée depuis le classeur transmis par la rédaction, feuille « APL 2024 », colonnes A (INSEE), B (nom), C (APL) et G (population standardisée). La géométrie et les voisins ne sont pas inventés. En cas de différence entre les codes DREES 2024 et le référentiel administratif de l’API Géo, l'application indique les codes sans correspondance.

## Sources

- DREES, *Accessibilité potentielle localisée aux professionnels de santé*, millésime 2024, publication 22 juillet 2026 : https://www.data.gouv.fr/datasets/accessibilite-potentielle-localisee-apl-aux-professionnels-de-sante
- Classeur **Indicateur d'APL aux médecins généralistes.xlsx** : https://data.drees.solidarites-sante.gouv.fr/explore/dataset/530_l-accessibilite-potentielle-localisee-apl/
- API Géo, contours administratifs publics : https://geo.api.gouv.fr/departements/85/communes?fields=nom,code&format=geojson&geometry=contour

La carte illustrant les intercommunalités de Vendée fournie par la rédaction n'est **pas** utilisée comme géométrie, car elle ne fournit pas de frontières par code INSEE exploitables. Le fond de la carte est constitué de polygones publics.

## Données et vérifications

Le fichier `donnees-vendee.json` contient déjà les 253 communes du millésime 2024 et leurs chiffres. **Aucune installation de Python ni traitement manuel n'est nécessaire pour publier cette version.** À l'ouverture de la page, le navigateur récupère en temps réel les polygones via l’API Géo et les associe par code INSEE. Les communes ne correspondant pas à cette source sont signalées dans les métadonnées de couverture de la page. En cas d’impossibilité d’accès au service, le message d’erreur propose un nouveau chargement.

La comparaison avec les voisines utilise les segments de bord réellement communs à deux polygones, et ne rapproche jamais les communes par le seul nom. Il faut confirmer ce calcul sur quelques cas tests. Les quintiles calculés sur les APL **des communes** sont des classes descriptives, et non des seuils de zonage officiel. Le classement concerne les communes, pas les habitants. Les ex æquo reçoivent le même rang. La comparaison des voisines présente une moyenne simple non pondérée.

**Pour une version intégralement autonome et plus robuste**, prévoir le téléchargement du GeoJSON de l'API Géo et l’intégration de ses géométries au JSON embarqué après vérification des codes INSEE, sans modification des chiffres DREES. L'API publique : `https://geo.api.gouv.fr/departements/85/communes?fields=nom,code&format=geojson&geometry=contour`.

## Prévisualiser et publier sur GitHub Pages

1. Pour prévisualiser localement, ouvrez un terminal dans le dossier et lancez `python -m http.server 8000`. Ouvrez `http://localhost:8000` (ne pas ouvrir directement `index.html` en `file://`).
2. Sur github.com, connectez-vous, cliquez sur **+** puis **New repository**.
3. Nommez-le `carte-medecins-vendee`, choisissez **Public**, cliquez **Create repository**.
4. Cliquez **uploading an existing file** ou **Add file → Upload files**. Déposez **index.html**, **style.css**, **script.js**, **donnees-vendee.json**, **README.md** (les outils Python ne sont pas nécessaires au site). Cliquez **Commit changes**.
5. Ouvrez **Settings → Pages**. Dans **Build and deployment**, choisissez **Deploy from a branch**, puis **main** et **/(root)**, cliquez **Save**.
6. L'URL typique est `https://VOTRE-PSEUDO.github.io/carte-medecins-vendee/`. Copiez l'adresse **exacte** affichée dans Settings → Pages.
7. Vérifiez sur ordinateur et téléphones avant de transmettre l'iframe au webmaster.

## Intégration iframe dans Alouette

Remplacez l'URL ci-dessous par celle affichée dans les paramètres GitHub Pages :

```html
<iframe src="https://VOTRE-PSEUDO.github.io/carte-medecins-vendee/" title="Carte interactive : accès aux médecins généralistes en Vendée, DREES 2024" width="100%" height="1900" loading="lazy" style="border:0;display:block;width:100%;max-width:100%" referrerpolicy="no-referrer-when-downgrade"></iframe>
```

Hauteur de départ suggérée : **1600 à 1900 px sur ordinateur**, **2200 à 2700 px sur mobile**, à ajuster après intégration au CMS et selon la largeur réelle (classements, textes et contenus font varier la hauteur). Une iframe externe ne s'ajuste pas automatiquement à la hauteur du contenu sans mécanisme spécifique côté site hôte : en cas de contenu coupé, augmentez la hauteur plutôt que de laisser un scroll interne inutilisable.

## Tests

**Exécutés automatiquement à la création :** syntaxe JavaScript avec Node (si disponible), compilation Python, validité JSON, présence des fichiers et liens internes. **Non exécutés :** comparaison visuelle de chaque valeur au classeur Excel, récupération et intégration effective des polygones (réseau sortant bloqué), tests interactifs Safari iOS / Chrome Android et audit des tailles d'écran 320/375/390/430/768/1440 px, test effectif d'iframe Alouette, mesures de performance réseau. Ces validations restent obligatoires après import officiel.

## Architecture

- `index.html` : page sémantique, libellés et source.
- `style.css` : responsive et accessibilité.
- `script.js` : Leaflet, survol, sélection, recherche, classement, comparateur.
- `donnees-vendee.json` : 253 données DREES intégrées ; géométries récupérées par l’API Géo dans le navigateur.
- `preparation_donnees.py` : utilitaire optionnel de préparation d’une version autonome avec géométries locales (nécessite Python et les dépendances).
- `requirements.txt` : dépendances Python de préparation uniquement.

La page ne collecte aucune donnée personnelle. Leaflet est chargé depuis un CDN public ; pour un hébergement intégralement autonome, il peut être téléchargé et servi localement en respectant sa licence.

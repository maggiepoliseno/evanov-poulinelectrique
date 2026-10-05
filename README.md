# Créatifs display Evanov · Evanov display creatives

**Poulin Électrique Inc** · https://evanov.poulinelectrique.com ([English](https://evanov.poulinelectrique.com/en/))

## Français

Page de téléchargement des créatifs display pour les deux IO d'Evanov Communications, en français, en anglais et en version bilingue.

- **IO 1 – Generac (balise A)** et **IO 2 – Poulin Électrique (balise B)**
- 72 fichiers : 36 JPG et 36 MP4, en 6 formats (300×250, 728×90, 160×600, 300×600, 970×250, 320×50), en français (`_FR_`), en anglais (`_EN_`) et bilingues (`_BI_`)
- Créatifs bilingues : le français est prédominant; la traduction anglaise, plus petite, occupe moins de la moitié de l'espace du texte français (Charte de la langue française, art. 58)
- MP4 : H.264, sans son, 14,5 s, moins de 200 Ko, joue une fois. Image de secours : le JPG du même format.
- `Static/` et `Video-MP4/` : les créatifs, classés par IO
- `PEI_Evanov_FR_CreativeList.csv` (séparateur « ; ») et `PEI_Evanov_EN_CreativeList.csv` : liste des créatifs avec les URL de clic
- `Proofs/` : épreuves des images fixes et des vidéos
- `PEI_Evanov_Display_2026-10.zip` : tous les créatifs display, les listes et les épreuves en un fichier
- `Logos/` : les logos utilisés sur le site
- `Facebook/` : publicité vidéo Facebook (Generac · entretien et service, 1920×1080, 18,7 s, avec son)
- `Final-Uploads/` : section « Versions finales déposées ». Toutes les 15 minutes, `.github/workflows/sync-final-uploads.yml` copie ici les fichiers du dossier Nextcloud du centre de dépôt (lien de partage « Autoriser l'envoi et la modification » : variable `FINAL_UPLOADS_SHARE` du dépôt ou `Final-Uploads/source.txt`)
- Commentaires : une boîte de commentaires sous chaque créatif (`assets/comments.js`). Les commentaires sont enregistrés par n8n (workflow « Evanov – Portal comments and uploads »), qui envoie un courriel à Maggie et un message dans Talk. Le même workflow supprime une version finale déposée (bouton « Supprimer », pour tout le monde) dans le Nextcloud et avise Maggie.


La page est publiée par GitHub Pages sur evanov.poulinelectrique.com (fichier `CNAME`). Elle n'est pas indexée par les moteurs de recherche.

## English

Download page for the display creatives for Evanov Communications' two IOs, in French, English and bilingual versions.

- **IO 1 – Generac (tag A)** and **IO 2 – Poulin Électrique (tag B)**
- 72 files: 36 JPG and 36 MP4, in 6 sizes (300×250, 728×90, 160×600, 300×600, 970×250, 320×50), in French (`_FR_`), English (`_EN_`) and bilingual (`_BI_`)
- Bilingual creatives: French is predominant; the smaller English translation takes less than half the space of the French text (Charter of the French Language, s. 58)
- MP4: H.264, no sound, 14.5 s, under 200 KB, plays once. Backup image: the JPG of the same size.
- `Static/` and `Video-MP4/`: the creatives, by IO
- `PEI_Evanov_EN_CreativeList.csv` and `PEI_Evanov_FR_CreativeList.csv` (";" separator): creative list with click-through URLs
- `Proofs/`: proofs of the static and video creatives
- `PEI_Evanov_Display_2026-10.zip`: all display creatives, lists and proofs in one file
- `Logos/`: the logos used on the site
- `Facebook/`: Facebook video ad (Generac · maintenance and service, 1920×1080, 18.7 s, with sound)
- `Final-Uploads/`: the "Final uploads" section. Every 15 minutes, `.github/workflows/sync-final-uploads.yml` copies the files of the upload centre's Nextcloud folder here (share link set to "Allow upload and editing": repository variable `FINAL_UPLOADS_SHARE` or `Final-Uploads/source.txt`)
- Comments: a comment box under each creative (`assets/comments.js`). Comments are saved by n8n (workflow "Evanov – Portal comments and uploads"), which emails Maggie and posts in Talk. The same workflow deletes a final upload ("Delete" button, for everyone) from Nextcloud and notifies Maggie.


The page is published by GitHub Pages at evanov.poulinelectrique.com (`CNAME` file). It is hidden from search engines.

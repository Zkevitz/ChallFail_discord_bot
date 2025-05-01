#!/usr/bin/env python3
"""
Name Recognition from Images
----------------------------
This script detects and extracts dates and times from images using OCR.
Optimized for detecting character names in Dofus game screenshots,
focusing on the game interface rather than combat logs.
"""

import cv2
import pytesseract
import os
import re
import argparse
from PIL import Image
import numpy as np

def preprocess_image(image):
    """
    Prétraite l'image pour améliorer la détection de texte
    """
    # Convertir en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Appliquer un flou gaussien pour réduire le bruit
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Améliorer le contraste avec CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blur)
    
    # Binarisation adaptative pour gérer les variations d'éclairage
    thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 11, 2)
    
    # Opérations morphologiques pour nettoyer l'image
    kernel = np.ones((1, 1), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Dilater légèrement le texte pour améliorer la connectivité
    dilated = cv2.dilate(opening, kernel, iterations=1)
    
    return dilated

def crop_image_regions(image, show_regions=False):
    """
    Découpe l'image en régions d'intérêt pour ignorer le chat de combat
    et se concentrer sur les zones où les noms de personnages apparaissent
    
    Args:
        image: L'image à découper
        show_regions: Si True, affiche les régions découpées
    """
    height, width = image.shape[:2]
    
    print(f"Dimensions de l'image originale: {width}x{height}")
    
    # Définir les régions d'intérêt (ROI)
    # Ces valeurs sont approximatives et peuvent nécessiter des ajustements
    
    # ROI 1: Chat in-game (en bas à gauche) - Élargi pour capturer plus de contenu
    # Augmenter la hauteur et la largeur pour capturer plus de messages
    roi_chat = image[int(height*0.6):height, 0:int(width*0.4)]
    
    # ROI 2: Partie centrale (excluant le chat en bas à gauche)
    roi_center = image[0:int(height*0.7), int(width*0.2):int(width*0.7)]
    
    regions = [roi_chat, roi_center]
    
    # Vérifier si les régions contiennent des données
    for i, region in enumerate(regions):
        r_height, r_width = region.shape[:2]
        print(f"Région {i+1}: dimensions {r_width}x{r_height}")
        
        # Vérifier si la région est entièrement noire
        is_black = np.all(region == 0)
        if is_black:
            print(f"ATTENTION: La région {i+1} est entièrement noire!")
        
        # Vérifier les valeurs min/max pour voir s'il y a du contenu
        min_val = np.min(region)
        max_val = np.max(region)
        print(f"Région {i+1}: valeurs min={min_val}, max={max_val}")
    
    # Afficher les régions si demandé
    if show_regions:
        region_names = ["Chat in-game", "Partie centrale"]
        for i, region in enumerate(regions):
            # Redimensionner la région si elle est trop grande
            max_height = 600
            r_height, r_width = region.shape[:2]
            if r_height > max_height:
                scale = max_height / r_height
                region_display = cv2.resize(region, (int(r_width * scale), max_height))
            else:
                region_display = region.copy()
            
            # Convertir en RGB si nécessaire (pour s'assurer que l'affichage est correct)
            if len(region_display.shape) == 2:  # Image en niveaux de gris
                region_display = cv2.cvtColor(region_display, cv2.COLOR_GRAY2BGR)
            elif region_display.shape[2] == 4:  # Image avec canal alpha
                region_display = cv2.cvtColor(region_display, cv2.COLOR_BGRA2BGR)
                
            # Afficher la région
            cv2.imshow(f'Région {i+1}: {region_names[i]}', region_display)
            
            # Sauvegarder la région pour débogage
            debug_path = f"region_{i+1}_{region_names[i].replace(' ', '_')}.png"
            cv2.imwrite(debug_path, region)
            print(f"Région {i+1} sauvegardée dans {debug_path}")
        
        print("Appuyez sur une touche pour fermer chaque fenêtre d'image...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return regions

def extract_text_from_image(image_path, lang='fra+eng'):
    """
    Extrait le texte d'une image en se concentrant sur les régions d'intérêt
    """
    try:
        # Charger l'image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Erreur: Impossible de charger l'image {image_path}")
            return ""
        
        # Découper l'image en régions d'intérêt
        regions = crop_image_regions(image)
        
        # Extraire le texte de chaque région
        all_text = ""
        for i, region in enumerate(regions):
            # Prétraitement de la région
            processed_region = preprocess_image(region)
            
            # Configuration de Tesseract pour améliorer la détection
            # Utiliser des guillemets simples pour éviter les problèmes d'échappement
            config = '--psm 6 --oem 3'
            
            # Utiliser Tesseract pour extraire le texte
            region_text = pytesseract.image_to_string(processed_region, lang=lang, config=config)
            
            # Ajouter le texte extrait avec un séparateur
            all_text += f"--- Région {i+1} ---\n{region_text}\n\n"
        
        return all_text
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte: {e}")
        return ""

def clean_ocr_text(line):
    """
    Corrige les erreurs OCR courantes pour faciliter la détection des dates et heures.
    Exemples :
    - Remplace les caractères ambigus en début de timestamp (L, I, 1, |) par [
    - Sépare les années collées à l'heure/minute (ex: 02:462025 -> 02:46 2025)
    """
    import re
    # Correction des crochets/timestamps
    line = re.sub(r'^[LI|]', '[', line)  # début de ligne ambigu
    line = re.sub(r'([ \(\|])([LI1|])(?=\d{1,2}[:\., ]?\d{2})', r'\1[', line)  # ailleurs, avant un timestamp
    # Correction des timestamps collés à l'année (ex: 02:462025)
    line = re.sub(r'(\d{1,2}[:\., ]\d{2})(\d{4})', r'\1 \2', line)
    # Correction des espaces manquants entre année et heure (ex: 2025 02:46)
    line = re.sub(r'(\d{4})(\d{1,2}[:\., ]\d{2})', r'\1 \2', line)
    return line

def detect_dates_and_times(text):
    """
    Détecte les dates et heures dans le texte du chat in-game
    Format attendu: [jour] [mois] [année] - [heure]:[minute]
    Exemple: "23 Martalo 655 10:12"
    """
    # Liste pour stocker les dates et heures détectées
    detected_dates = []
    # Diviser le texte en lignes
    lines = text.split('\n')
    # Dictionnaire de conversion des mois Dofus vers les mois standard
    dofus_months = {
        'Javian': 'Janvier',
        'Flovor': 'Février',
        'Martalo': 'Mars',
        'Aperirel': 'Avril',
        'Maimayer': 'Mai',
        'Juinssidor': 'Juin',
        'Jouillier': 'Juillet',
        'Fraouctor': 'Août',
        'Septange': 'Septembre',
        'Octolliard': 'Octobre',
        'Novamaire': 'Novembre',
        'Décembire': 'Décembre'
    }
    # Pattern pour détecter les dates au format Dofus
    # Format: [jour] [mois] [année] [heure]:[minute] (année séparée ou collée)
    date_pattern = re.compile(r'(\d+)\s+([A-Za-zéèêëàâäôöùûüÿçÉÈÊËÀÂÄÔÖÙÛÜŸÇ]+)\s+(\d{4})\s+(\d{1,2}):(\d{2})')
    # Pattern pour détecter les timestamps simples [HH:MM]
    timestamp_pattern = re.compile(r'\[(\d+):(\d+)\]')
    # Pattern plus tolérant pour les timestamps avec erreurs d'OCR potentielles
    ocr_timestamp_pattern = re.compile(r'[\[\|\(]?\s*(\d{1,4})[\:\.\,\s]*(\d{2})[\]\)\|]?')
    for line in lines:
        # Nettoyage OCR
        clean_line = clean_ocr_text(line)
        # Ignorer les lignes vides ou trop courtes
        if len(clean_line.strip()) < 3:
            continue
        # Chercher les dates au format Dofus
        date_matches = date_pattern.findall(clean_line)
        for match in date_matches:
            if len(match) == 5:  # jour, mois, année, heure, minute
                day, month_dofus, year, hour, minute = match
                # Convertir le mois Dofus en mois standard si possible
                month = dofus_months.get(month_dofus, month_dofus)
                date_str = f"{day} {month} {year} {hour}:{minute}"
                detected_dates.append({
                    'date_str': date_str,
                    'day': int(day),
                    'month': month,
                    'month_dofus': month_dofus,
                    'year': int(year),
                    'hour': int(hour),
                    'minute': int(minute),
                    'original_text': clean_line.strip()
                })
        # Chercher les timestamps simples
        timestamp_matches = timestamp_pattern.findall(clean_line)
        for match in timestamp_matches:
            if len(match) == 2:  # heure, minute
                hour, minute = match
                # Vérifier si c'est un timestamp valide
                if 0 <= int(hour) <= 23 and 0 <= int(minute) <= 59:
                    timestamp_str = f"{hour}:{minute}"
                    detected_dates.append({
                        'timestamp': timestamp_str,
                        'hour': int(hour),
                        'minute': int(minute),
                        'original_text': clean_line.strip()
                    })
        # Chercher les timestamps avec erreurs d'OCR potentielles
        ocr_timestamp_matches = ocr_timestamp_pattern.findall(clean_line)
        for match in ocr_timestamp_matches:
            if len(match) == 2:  # heure, minute
                hour_str, minute = match
                try:
                    # Gérer le cas où le crochet "[" est interprété comme "1"
                    # Par exemple, "10246" pourrait être "[02:46]"
                    if len(hour_str) >= 3 and hour_str.startswith('1'):
                        potential_hour = hour_str[1:]
                        if len(potential_hour) == 2:
                            hour_int = int(potential_hour)
                            if 0 <= hour_int <= 23:
                                minute_int = int(minute)
                                if 0 <= minute_int <= 59:
                                    timestamp_str = f"{hour_int:02d}:{minute_int:02d}"
                                    detected_dates.append({
                                        'timestamp': timestamp_str,
                                        'hour': hour_int,
                                        'minute': minute_int,
                                        'original_text': clean_line.strip(),
                                        'ocr_corrected': True,
                                        'correction_note': f"Corrigé de '{hour_str}:{minute}' à '{hour_int:02d}:{minute_int:02d}'"
                                    })
                                    continue
                    # Traitement standard
                    hour_int = int(hour_str)
                    minute_int = int(minute)
                    # Vérifier si c'est un timestamp valide
                    if 0 <= hour_int <= 23 and 0 <= minute_int <= 59:
                        timestamp_str = f"{hour_int}:{minute_int:02d}"
                        # Éviter les doublons (si déjà détecté par le pattern standard)
                        is_duplicate = False
                        for date in detected_dates:
                            if 'timestamp' in date and date['timestamp'] == timestamp_str and date['original_text'] == clean_line.strip():
                                is_duplicate = True
                                break
                        if not is_duplicate:
                            detected_dates.append({
                                'timestamp': timestamp_str,
                                'hour': hour_int,
                                'minute': minute_int,
                                'original_text': clean_line.strip(),
                                'ocr_corrected': True
                            })
                except ValueError:
                    # Ignorer si les valeurs ne sont pas des nombres valides
                    pass
    return detected_dates

def process_image(image_path, output_path=None, show_image=False):
    """
    Traite une image pour en extraire les dates et heures
    """
    # Charger l'image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Erreur: Impossible de charger l'image {image_path}")
        return []
        
    # Découper l'image en régions d'intérêt
    regions = crop_image_regions(image, show_image)
    
    # Extraire le texte
    text = extract_text_from_image(image_path)
    
    # Afficher le texte brut extrait
    print("Texte extrait:")
    print("-" * 40)
    print(text)
    print("-" * 40)
    
    # Détecter les dates et heures
    dates = detect_dates_and_times(text)
    
    # Afficher les dates et heures détectées
    print("\nDates et heures détectées:")
    print("-" * 40)
    if dates:
        for date_info in dates:
            if 'date_str' in date_info:
                print(f"- Date complète: {date_info['date_str']}")
                print(f"  Jour: {date_info['day']}, Mois: {date_info['month']} ({date_info['month_dofus']}), Année: {date_info['year']}")
                print(f"  Heure: {date_info['hour']}:{date_info['minute']:02d}")
                print(f"  Texte original: {date_info['original_text']}")
            else:
                print(f"- Timestamp: {date_info['timestamp']}")
                if 'correction_note' in date_info:
                    print(f"  Note: {date_info['correction_note']}")
                print(f"  Texte original: {date_info['original_text']}")
            print()
    else:
        print("Aucune date ou heure détectée.")
    print("-" * 40)
    
    # Afficher l'image avec les zones de texte détectées si demandé
    if show_image:
        # Créer une copie de l'image pour le dessin
        vis_image = image.copy()
        
        # Dessiner les contours des régions
        height, width = image.shape[:2]
        colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0)]  # Vert, Rouge, Bleu
        cv2.rectangle(vis_image, (0, int(height*0.6)), (int(width*0.4), height), colors[0], 2)  # ROI 1: Chat (élargi)
        cv2.rectangle(vis_image, (int(width*0.2), 0), (int(width*0.7), int(height*0.7)), colors[1], 2)  # ROI 2: Centre
        
        # Redimensionner l'image pour l'affichage si elle est trop grande
        max_height = 800
        if height > max_height:
            scale = max_height / height
            vis_image = cv2.resize(vis_image, (int(width * scale), max_height))
        
        # Afficher l'image
        cv2.imshow('Régions analysées (image complète)', vis_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    # Sauvegarder les résultats si un chemin de sortie est spécifié
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("Texte extrait:\n")
            f.write("-" * 40 + "\n")
            f.write(text + "\n")
            f.write("-" * 40 + "\n\n")
            
            f.write("Dates et heures détectées:\n")
            f.write("-" * 40 + "\n")
            if dates:
                for date_info in dates:
                    if 'date_str' in date_info:
                        f.write(f"- Date complète: {date_info['date_str']}\n")
                        f.write(f"  Jour: {date_info['day']}, Mois: {date_info['month']} ({date_info['month_dofus']}), Année: {date_info['year']}\n")
                        f.write(f"  Heure: {date_info['hour']}:{date_info['minute']:02d}\n")
                        f.write(f"  Texte original: {date_info['original_text']}\n")
                    else:
                        f.write(f"- Timestamp: {date_info['timestamp']}\n")
                        if 'correction_note' in date_info:
                            f.write(f"  Note: {date_info['correction_note']}\n")
                        f.write(f"  Texte original: {date_info['original_text']}\n")
                    f.write("\n")
            else:
                f.write("Aucune date ou heure détectée.\n")
            f.write("-" * 40 + "\n")
        
        print(f"\nRésultats sauvegardés dans {output_path}")
    
    return dates

def main():
    # Configurer l'analyseur d'arguments
    parser = argparse.ArgumentParser(description='Détection de dates et heures dans des images de chat Dofus')
    parser.add_argument('image_path', help='Chemin vers l\'image à analyser')
    parser.add_argument('-o', '--output', help='Chemin pour sauvegarder les résultats')
    parser.add_argument('-s', '--show', action='store_true', help='Afficher l\'image avec les zones de texte détectées')
    parser.add_argument('-r', '--regions', action='store_true', help='Afficher les régions découpées individuellement')
    
    # Analyser les arguments
    args = parser.parse_args()
    
    # Traiter l'image
    image = cv2.imread(args.image_path)
    if image is None:
        print(f"Erreur: Impossible de charger l'image {args.image_path}")
        return
        
    # Afficher les régions découpées si demandé
    if args.regions:
        crop_image_regions(image, show_regions=True)
    
    # Traiter l'image
    process_image(args.image_path, args.output, args.show)

if __name__ == "__main__":
    main()

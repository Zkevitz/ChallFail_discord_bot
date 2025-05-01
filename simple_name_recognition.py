#!/usr/bin/env python3
"""
Simple Name Recognition from Images
-----------------------------------
This script uses available system packages to detect names in images.
"""

import os
import re
import argparse
import subprocess
from pathlib import Path

def extract_text_with_tesseract(image_path, lang='fra+eng'):
    """
    Utilise Tesseract directement via subprocess pour extraire le texte d'une image
    """
    try:
        # Vérifier si l'image existe
        if not os.path.isfile(image_path):
            print(f"Erreur: L'image {image_path} n'existe pas")
            return ""
        
        # Appeler Tesseract via subprocess
        result = subprocess.run(
            ['tesseract', image_path, 'stdout', '-l', lang],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Récupérer la sortie
        text = result.stdout
        
        return text
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de Tesseract: {e}")
        print(f"Sortie d'erreur: {e.stderr}")
        return ""
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte: {e}")
        return ""

def detect_names(text):
    """
    Détecte les noms potentiels dans le texte
    Utilise plusieurs heuristiques pour identifier les noms
    """
    # Liste pour stocker les noms détectés
    detected_names = []
    
    # Diviser le texte en lignes
    lines = text.split('\n')
    
    # Expressions régulières pour détecter les formats de noms courants
    # Cette regex détecte les mots commençant par une majuscule
    name_pattern = re.compile(r'\b[A-Z][a-zéèêëàâäôöùûüÿçÉÈÊËÀÂÄÔÖÙÛÜŸÇ]+\b')
    
    # Regex pour détecter les formats "Nom: Valeur" ou "Nom - Valeur"
    label_pattern = re.compile(r'\b(Nom|Name|Joueur|Player|Utilisateur|User)\s*[:|-]\s*([A-Za-zéèêëàâäôöùûüÿçÉÈÊËÀÂÄÔÖÙÛÜŸÇ]+)')
    
    for line in lines:
        # Chercher les motifs de type "Nom: Valeur"
        label_matches = label_pattern.findall(line)
        for match in label_matches:
            detected_names.append(match[1].strip())
        
        # Si aucun motif de label n'est trouvé, chercher des mots commençant par une majuscule
        if not label_matches:
            # Filtrer les mots courts (moins de 3 caractères) et les mots courants
            common_words = ['Le', 'La', 'Les', 'Un', 'Une', 'Des', 'The', 'A', 'An']
            name_matches = name_pattern.findall(line)
            for name in name_matches:
                if len(name) >= 3 and name not in common_words:
                    detected_names.append(name)
    
    # Supprimer les doublons
    detected_names = list(set(detected_names))
    
    return detected_names

def process_image(image_path, output_path=None):
    """
    Traite une image pour en extraire les noms
    """
    # Extraire le texte
    text = extract_text_with_tesseract(image_path)
    
    # Afficher le texte brut extrait
    print("Texte extrait:")
    print("-" * 40)
    print(text)
    print("-" * 40)
    
    # Détecter les noms
    names = detect_names(text)
    
    # Afficher les noms détectés
    print("\nNoms potentiels détectés:")
    print("-" * 40)
    if names:
        for name in names:
            print(f"- {name}")
    else:
        print("Aucun nom détecté.")
    print("-" * 40)
    
    # Sauvegarder les résultats si un chemin de sortie est spécifié
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("Texte extrait:\n")
            f.write("-" * 40 + "\n")
            f.write(text + "\n")
            f.write("-" * 40 + "\n\n")
            
            f.write("Noms potentiels détectés:\n")
            f.write("-" * 40 + "\n")
            if names:
                for name in names:
                    f.write(f"- {name}\n")
            else:
                f.write("Aucun nom détecté.\n")
            f.write("-" * 40 + "\n")
        
        print(f"\nRésultats sauvegardés dans {output_path}")
    
    return names

def process_directory(directory_path, output_dir=None):
    """
    Traite toutes les images dans un répertoire
    """
    # Créer le répertoire de sortie s'il n'existe pas
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Extensions d'images supportées
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    # Compteur pour les statistiques
    processed_count = 0
    success_count = 0
    
    # Parcourir tous les fichiers du répertoire
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        # Vérifier si c'est un fichier et s'il a une extension d'image
        if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in image_extensions):
            processed_count += 1
            print(f"\nTraitement de l'image {processed_count}: {filename}")
            
            # Définir le chemin de sortie si nécessaire
            output_path = None
            if output_dir:
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(output_dir, f"{base_name}_results.txt")
            
            # Traiter l'image
            try:
                names = process_image(file_path, output_path)
                if names:
                    success_count += 1
            except Exception as e:
                print(f"Erreur lors du traitement de {filename}: {e}")
    
    # Afficher les statistiques
    print("\n" + "=" * 50)
    print(f"Traitement terminé. {processed_count} images traitées.")
    if processed_count > 0:
        print(f"Noms détectés dans {success_count} images ({success_count/processed_count*100:.1f}% de réussite).")
    print("=" * 50)

def main():
    # Configurer l'analyseur d'arguments
    parser = argparse.ArgumentParser(description='Détection de noms dans des images')
    parser.add_argument('path', help='Chemin vers l\'image ou le répertoire à analyser')
    parser.add_argument('-o', '--output', help='Chemin pour sauvegarder les résultats')
    
    # Analyser les arguments
    args = parser.parse_args()
    
    # Vérifier si le chemin est un fichier ou un répertoire
    path = Path(args.path)
    if path.is_file():
        # Traiter une seule image
        process_image(str(path), args.output)
    elif path.is_dir():
        # Traiter un répertoire d'images
        process_directory(str(path), args.output)
    else:
        print(f"Erreur: {args.path} n'est ni un fichier ni un répertoire valide.")

if __name__ == "__main__":
    main()

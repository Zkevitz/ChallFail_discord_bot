#!/usr/bin/env python3
"""
Batch Name Recognition
---------------------
Process multiple images to extract names.
"""

import os
import argparse
from name_recognition import process_image

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
    print(f"Noms détectés dans {success_count} images ({success_count/processed_count*100:.1f}% de réussite).")
    print("=" * 50)

def main():
    # Configurer l'analyseur d'arguments
    parser = argparse.ArgumentParser(description='Détection de noms dans plusieurs images')
    parser.add_argument('directory', help='Répertoire contenant les images à analyser')
    parser.add_argument('-o', '--output', help='Répertoire pour sauvegarder les résultats')
    
    # Analyser les arguments
    args = parser.parse_args()
    
    # Traiter le répertoire
    process_directory(args.directory, args.output)

if __name__ == "__main__":
    main()

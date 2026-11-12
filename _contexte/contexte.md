# Contexte — creation_3d

## Objectif (immuable sauf décision explicite)
Projet pour créer des animations 3D

## Stack / contraintes techniques (stable, rarement modifié)
- RTX 4060 8 Go, Ryzen 7 5700X, 48 Go RAM ; installations sur D:.
- Blender 4.5.13 + MPFB 2.0.17, Kimodo (`D:\AI\kimodo`, SOMA-RP v1.2), Godot 4.5, Unreal 5.7. Pas de Unity.
- Exports : GLB (pivot) + FBX. Accord utilisateur avant chaque usage GPU (`python run.py vram`).

## État actuel (réécrit intégralement à chaque /close)
Phases 0 à 2 terminées. Pipeline de bout en bout fonctionnel : MPFB2 → Kimodo → retarget → GLB/FBX → rendu Cycles.
Imports Godot et Unreal passés ; rendu #3 validé dans l'artefact.
Défauts connus : tête trop relevée, iris rougeâtre, orchestration `run.py` absente.
Prochaine phase : 3, benchmark de génération 3D.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-11-08 : Initialisation du protocole vibecoding.
- 2026-11-12 : Humain réaliste via MPFB2 et mouvement via Kimodo (text-to-motion) retargeté sous Blender, plutôt qu'image vers 3D + UniRig.
- 2026-11-12 : Export glTF avec `export_apply=True` (sinon la géométrie d'aide MPFB est exportée).

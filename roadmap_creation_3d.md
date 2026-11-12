# Roadmap — creation_3d : protocole local de création et d'animation 3D

Objectif : un protocole reproductible qui génère des modèles 3D puis les anime, avec la meilleure qualité possible sur le matériel disponible, en n'utilisant que des IA locales.

## Contraintes de départ (relevé du 2026-11-08)
- GPU : NVIDIA GeForce RTX 4060, 8 Go de VRAM (1,5 Go déjà occupés au moment du relevé), pilote 610.88.
- CPU : AMD Ryzen 7 5700X (8 cœurs). RAM : 48 Go. D: : 1,5 To libres.
- Déjà présents sur D: :
  - Blender 4.5.13 (`D:\Blender-4.5.13`) et Blender dans `D:\blender` (contient un dossier `5.2`, version à confirmer) ;
  - Godot (`D:\Godot`) ;
  - image vers 3D : TripoSR (`D:\AI\TripoSR`), Stable Fast 3D (`D:\tools\stable-fast-3d`) ;
  - rigging automatique : UniRig (`D:\AI\UniRig`) ;
  - vidéo et mouvement 2D : MimicMotion (`D:\AI\MimicMotion`), WanGP (`D:\AI\WanGP`) ;
  - génération d'images : ComfyUI-Qwen, ComfyUI-SANA, Flux (`D:\ServOMorph\...`) ;
  - LLM et VLM via Ollama : qwen2.5vl, llava:7b, gemma3/gemma4, qwen3.5, mistral-nemo, etc. ;
  - caches Hugging Face : `D:\HuggingFaceCache`, `D:\ai-cache`.
- Moteurs cibles : Godot est présent (`D:\Godot`). Unreal Engine 5.7 est installé (`D:\Epic Games\UE_5.7`, confirmé par l'utilisateur). Unity : ne pas l'installer (consigne de l'utilisateur). Il n'est installé ni dans `C:\Program Files\Unity\Hub\Editor` ni sur D: (dossiers racine contrôlés).
- Export obligatoire : chaque modèle animé doit s'importer dans Godot, Unreal et Unity. Format pivot : glTF 2.0 binaire (`.glb`), avec un export FBX en complément pour Unreal et Unity. Conventions communes : 1 unité = 1 m, axe Y en haut, squelette humanoïde nommé de façon compatible avec le retargeting des moteurs, clips d'animation nommés.
- VRAM : avant chaque lancement sur le GPU, demander l'accord de l'utilisateur en indiquant l'outil, la VRAM estimée et la VRAM libre relevée par `nvidia-smi`. Pas de verrou automatique entre les sessions.
- Rôle de Claude : orchestrateur. Les modèles qui génèrent, rigguent, animent et évaluent tournent en local. Le passage de rendus par le cloud est accepté par l'utilisateur.

## Pipeline cible (hypothèse de travail, remise en cause en phase 1)
texte → image de référence (ComfyUI) → maillage texturé (image vers 3D) → nettoyage et retopologie (Blender en mode headless) → rig (UniRig) → mouvement (text-to-motion, vidéo vers mouvement ou procédural) → retargeting (Blender) → rendu (Eevee ou Cycles) → évaluation (VLM local + tes commentaires dans l'artefact).

---

## Phase 0 — Référence réaliste sans outils et socle [FAIT]
- Créer dans l'artefact la scène animée la plus réaliste possible, entièrement codée à la main (Three.js, sans IA ni Blender). Elle sert d'étalon de qualité pour la suite.
- Recueillir les commentaires de l'utilisateur sur cette référence.
- Mettre en place la structure du projet : `assets/` (sorties générées, hors git), `pipeline/` (scripts par étape), `bench/` (cas verrouillés), `artefact/` (page de revue), `run.py`.
- Écrire `pipeline/vram.py` : relevé de la VRAM libre et liste des processus GPU via `nvidia-smi`, affichés dans la demande d'accord avant chaque lancement.
- Tests : `vram.py` renvoie des valeurs cohérentes avec `nvidia-smi`.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 1 — Veille et sélection des outils [FAIT]
- Recenser les candidats pour chaque étape : image vers 3D, texte vers 3D, texturage, retopologie, auto-rig, text-to-motion, vidéo vers mouvement, rendu.
- Critères : tenue en 8 Go de VRAM (avec offload CPU ou quantification), qualité, licence, maintenance, installation sous Windows, durée par asset.
- Vérifier l'état réel des outils déjà installés (environnements, poids téléchargés, lancement).
- Livrable : `_docs/comparatif_outils.md`, avec un choix principal et un repli par étape.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 2 — Pipeline minimal de bout en bout [FAIT]
- Enchaîner l'étape la plus simple à chaque niveau : image vers 3D (outil retenu), rig automatique, animation procédurale (marche ou idle), rendu Eevee de 5 s en MP4.
- Orchestration par `run.py` ; chaque étape GPU attend l'accord de l'utilisateur.
- Exporter en `.glb` et en `.fbx`.
- Publier le rendu dans l'artefact pour avoir tes premiers commentaires.
- Tests : exécution complète, sorties présentes à chaque étape, import headless du `.glb` dans Godot sans erreur (animation lue), import dans Unreal 5.7 par script Python de l'éditeur. Unity : test reporté tant qu'il n'est pas installé.
- Réalisé (2026-11-12) : MPFB2 + Kimodo à la place de image vers 3D + UniRig, rendu Cycles CPU. Tests Godot et Unreal passés, rendu #3 validé par l'utilisateur. Reporté : l'orchestration par `run.py` (seule la commande `vram` existe).

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 3 — Benchmark de génération 3D [EN COURS]
- Verrouiller 6 cas : personnage humanoïde, animal, objet rigide, véhicule, créature stylisée, personnage cartoon.
- Comparer les outils de la phase 1 sur ces cas : qualité du maillage, texture, topologie, VRAM maximale, durée.
- Gate : benchmark reproductible (mêmes entrées, mêmes seeds), avec un score VLM local et ta note.
- Livrable : planche comparative dans l'artefact et choix de l'outil par défaut.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 4 — Rigging et animation [TODO]
- Rig automatique (UniRig, puis les alternatives retenues) et contrôle des poids de skinning.
- Sources de mouvement : text-to-motion local, extraction depuis une vidéo (pose estimation), bibliothèque procédurale Blender.
- Retargeting vers le rig généré, avec correction du glissement des pieds et des interpénétrations.
- Tests : 3 animations de test (marche, saut, geste) sur 2 modèles de la phase 3.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 5 — Rendu et qualité visuelle [TODO]
- Comparer Eevee et Cycles (OptiX, débruitage) en temps de rendu par image et en qualité sur une RTX 4060.
- Préparer des presets d'éclairage, de caméra, de matériaux et d'étalonnage.
- Optionnel : passe d'amélioration vidéo locale (upscale, interpolation) si elle tient en VRAM.
- Gate : rendu de référence verrouillé, avec comparaison avant/après dans l'artefact.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 6 — Boucle d'amélioration [TODO]
- Lire tes commentaires dans l'artefact, puis classer chaque retour par étape du pipeline.
- Ajouter une évaluation automatique par un VLM local (qwen2.5vl) : grille de défauts fixe, score par rendu.
- Itérer sur les paramètres de chaque étape et historiser les versions (paramètres, scores, rendu).
- Gate : amélioration mesurée sur les cas verrouillés par rapport à la phase 5.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 7 — Protocole final [TODO]
- Rédiger le protocole dans `_docs/protocole.md` : étapes, outils, presets, budget VRAM par étape, durée par asset.
- Une commande lance tout le pipeline (`run.py "<description>"`), avec reprise après échec à chaque étape.
- Tests : génération complète de 2 nouveaux sujets jamais vus, puis import et lecture des animations dans Godot, Unreal et Unity.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

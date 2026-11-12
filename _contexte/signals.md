# Signals — creation_3d   (MAJ 2026-11-12)

## Actions ouvertes
<!-- ≤ 20 entrées (ligne « Backlog » exclue) ; dette et findings non urgents -> _contexte/backlog.md -->
- [P1|ouvert] Démarrer la phase 3 (benchmark de génération 3D, 6 cas verrouillés)
  - fait quand: les 6 cas et leurs entrées sont figés dans `bench/` avec seeds.
  - réf: `roadmap_creation_3d.md` (phase 3), `_docs/comparatif_outils.md`.
- [P2|ouvert] Corriger la tête du personnage, qui regarde trop haut après le retarget
  - fait quand: la tête est droite dans le rendu de marche, validée par l'utilisateur.
  - réf: `pipeline/retarget_soma.py` (DIR_CHILD, tgt_ref).
- [P2|ouvert] Orchestrer le pipeline par `run.py` (seule la commande `vram` existe)
  - fait quand: `run.py` enchaîne MPFB → Kimodo → retarget → export → rendu avec accord VRAM par étape GPU.
  - réf: `run.py`, `pipeline/`.
- Backlog : 2 entrées (dette 1, amélioration 1) — `_contexte/backlog.md`

## Contexte chaud
- Accès Llama-3-8B-Instruct (gated) accordé ; poids en cache dans `D:\HuggingFaceCache`, encodeur texte Kimodo sur CPU (~16 Go RAM).
- Artefact de revue : https://claude.ai/artifact/LyvdLM1nFQbo3GkzfKCST2 (rendu #3 validé le 2026-11-12).
- Mode /telephone utilisé cette session.

## Dernière session (2026-11-12)
# Session du 2026-11-12

## Décisions prises
- Pipeline phase 2 : MPFB2 (humain) + Kimodo SOMA (mouvement texte) + retarget Blender, au lieu d'image vers 3D + UniRig.
- Rendu Cycles CPU (GPU occupé par d'autres projets) ; export glTF avec `export_apply=True` obligatoire.
- Kimodo : conversion BVH avec `--bvh_standard_tpose` pour le retarget.

## Livrables produits ou modifiés
- `pipeline/mpfb_human.py`, `render_still.py`, `render_anim.py`, `retarget_soma.py`, `export_web.py` : créés.
- `bench/godot_import/`, `bench/ue_import/` : tests d'import, passés.
- `artefact/index.html` : rendu #3 avec visionneuse 3D orbitale, publié.
- `roadmap_creation_3d.md` : phases 0 à 2 [FAIT], phase 3 [EN COURS].

## Hypothèses validées / invalidées
- VALIDE : Kimodo tient en 8 Go (pic relevé 2 353 Mio).
- VALIDE : GLB lu par Godot 4.5, FBX importé par UE 5.7 (149 images, 54 os, 9 matériaux).
- INVALIDE : BVH Kimodo par défaut -> pivot vers `--bvh_standard_tpose`.

## Prochaine étape exacte
Démarrer la phase 3 : figer les 6 cas du benchmark.

## Question bloquante pour la session suivante
Aucune

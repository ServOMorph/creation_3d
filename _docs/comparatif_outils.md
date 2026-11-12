# Comparatif des outils — phase 1 (2026-11-08)

Objectif : améliorer le rendu #2 (humain en marche codé à la main) avec des outils locaux, sur une RTX 4060 de 8 Go.
Légende des chiffres de VRAM : « relevé » = mesuré ici ; « annoncé » = source tierce, non vérifié.

## 1. État des outils installés (contrôlé le 2026-11-08)

| Outil | Environnement | Poids | État |
|---|---|---|---|
| TripoSR | `.venv`, torch 2.11 cu128, CUDA OK | `models--stabilityai--TripoSR` | opérationnel |
| Stable Fast 3D | `.venv`, torch 2.7.1 cu128, CUDA OK | `D:\ai-cache\...\stable-fast-3d` | dernier run réussi (`SF3D_OK`, 7 510 sommets) |
| UniRig | aucun venv trouvé (ni dans les 3 venvs, ni dans le Python global) | `models--VAST-AI--UniRig` | sorties existantes (`results/nino_*.glb`) ; environnement à retrouver |
| MimicMotion | `.venv`, torch 2.5.1 cu121, CUDA OK | `models/` | opérationnel (vidéo 2D) |
| WanGP | `env_uv`, torch 2.10 cu130, CUDA OK | `ckpts/` | opérationnel (vidéo 2D) |

Retour d'expérience du projet « Jeu pour Nino » (`game_art/_contexte/contexte.md`) : MimicMotion, Wan Animate, SD1.5, Flux et le rendu direct TripoSR + UniRig ont produit des candidats, tous rejetés visuellement. Le rig UniRig (28 os) était cohérent, mais le maillage TripoSR ne tenait pas en rendu direct.

## 2. Constat principal

Pour un humain réaliste, la qualité vient de trois points : un maillage à topologie propre (visage, articulations), un vrai mouvement capturé et un rendu physique. Les générateurs image vers 3D (TripoSR, SF3D, TRELLIS.2) produisent des surfaces « figées » : topologie triangulée sans boucles, vêtements fondus dans le corps, visage flou. Elles se riggent mal. Ils restent utiles pour les objets, les accessoires et les créatures, pas comme base d'un humain animé.

## 3. Candidats par étape

### Modèle humain
- **MPFB2 (MakeHuman pour Blender)**, v2.0.17 (juillet 2026), Blender 4.2+. Corps paramétrique avec topologie propre, peau, yeux, cheveux, vêtements, rig standard ou Rigify, CPU seulement, licence CC0 pour les assets. Avis signalant un problème sous 4.5 (version 2.0.15) : à tester.
- SAM 3D Body (Meta) : corps humain depuis une image, licence et VRAM à vérifier.
- Repli : TRELLIS.2 (qualité de surface et PBR, environ 6,2 Go annoncés à 512 en mode low-VRAM) ou SF3D (déjà installé) pour les vêtements et accessoires.

### Mouvement
- **HY-Motion 1.0 Lite** (Tencent) : text-to-motion, environ 4 Go annoncés pour le modèle et 4 Go pour l'encodeur Qwen3-8B en int4. Cela tient juste dans 8 Go, à mesurer.
- **Kimodo** (NVIDIA, v1.1, avril 2026) : text-to-motion avec contraintes (images clés, trajectoires), checkpoints SOMA sous licence NVIDIA Open Model (usage commercial autorisé, selon une source communautaire). Avec `TEXT_ENCODER_DEVICE=cpu`, la VRAM annoncée descend sous 3 Go.
- **GVHMR** : mouvement depuis une vidéo (SMPL-X, repère monde). Licence non commerciale ; SMPL-X demande une inscription au MPI.
- Repli : la marche procédurale actuelle (IK, déjà écrite) ou la bibliothèque CMU mocap (BVH, domaine public), à retargeter.

### Rig et retargeting
- **Rig MPFB2 (Rigify)** si le modèle vient de MPFB2 : pas d'auto-rig nécessaire.
- UniRig pour les maillages générés (licence permissive, environnement à retrouver).
- Make-It-Animatable (humanoïdes, rapide) : repli à évaluer.
- Retargeting : Blender en mode headless (mapping SMPL-X ou SOMA vers Rigify), puis correction du contact des pieds.

### Rendu
- **Blender 4.5 Cycles** (OptiX et débruitage OIDN) pour la référence ; Eevee pour les itérations rapides.
- Export GLB et FBX pour Godot et Unreal ; l'artefact Three.js lit le GLB.

## 4. Choix proposé pour la phase 2

MPFB2 (humain rigué) → HY-Motion Lite ou Kimodo (marche générée) → retargeting Blender → rendu Cycles en MP4 et export GLB affiché dans l'artefact.

| Étape | Principal | Repli | GPU |
|---|---|---|---|
| Humain | MPFB2 | SF3D/TRELLIS.2 + UniRig | non / oui |
| Mouvement | Kimodo (encodeur sur CPU) | HY-Motion Lite, puis CMU BVH | oui |
| Rig | Rigify MPFB2 | UniRig | non |
| Rendu | Cycles OptiX | Eevee | oui |

Décision de l'utilisateur (2026-11-08) : MPFB2 + Kimodo retenus pour la phase 2.

## 5. Points ouverts
- Environnement Python d'UniRig : introuvable, demander à l'utilisateur.
- VRAM réelle de Kimodo et de HY-Motion Lite : à mesurer après accord.
- Compatibilité de MPFB2 avec Blender 4.5.13 : à tester (sans GPU).
- Licences : GVHMR et SMPL-X sont non commerciaux ; à écarter si l'usage devient commercial.

## Sources
- https://github.com/makehumancommunity/mpfb2 ; https://extensions.blender.org/add-ons/mpfb/
- https://rits.shanghai.nyu.edu/ai/nvidia-releases-kimodo-controllable-text-to-motion-for-characters-and-humanoid-robots/ ; https://huggingface.co/spaces/nvidia/Kimodo/blob/main/README.md
- https://rits.shanghai.nyu.edu/ai/tencent-open-sources-hy-motion-1-0-a-billion-parameter-text-to-motion-ai-model/ ; https://www.sourcepulse.org/projects/25967472
- https://trellis2.app/blog/trellis-2-low-vram
- https://pypi.org/project/gvhmr/ ; https://github.com/PozzettiAndrea/ComfyUI-MotionCapture
- https://arxiv.org/html/2504.12451 (UniRig)

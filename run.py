import argparse
import sys

from pipeline import vram


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="creation_3d : orchestrateur du pipeline 3D local")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("vram", help="Afficher l'état GPU et la demande d'accord")
    p.add_argument("--outil", default="outil non précisé")
    p.add_argument("--estime", type=int, default=0, help="VRAM estimée en Mio")
    args = parser.parse_args()
    if args.cmd == "vram":
        print(vram.approval_request(args.outil, args.estime))


if __name__ == "__main__":
    main()

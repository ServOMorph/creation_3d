import subprocess
import sys
from dataclasses import dataclass


@dataclass
class GpuState:
    name: str
    total_mib: int
    used_mib: int
    free_mib: int


@dataclass
class GpuProcess:
    pid: int
    name: str
    used_mib: int


def _smi(args):
    out = subprocess.run(["nvidia-smi", *args], capture_output=True, text=True, check=True)
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def gpu_state():
    line = _smi(["--query-gpu=name,memory.total,memory.used,memory.free", "--format=csv,noheader,nounits"])[0]
    name, total, used, free = [p.strip() for p in line.split(",")]
    return GpuState(name, int(total), int(used), int(free))


def gpu_processes():
    procs = []
    for line in _smi(["--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader,nounits"]):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            continue
        pid, name, mem = parts
        procs.append(GpuProcess(int(pid), name, int(mem) if mem.isdigit() else 0))
    return procs


def approval_request(tool, estimated_mib):
    st = gpu_state()
    lines = [
        f"Demande d'accord GPU : {tool}",
        f"VRAM estimée : {estimated_mib} Mio",
        f"VRAM libre : {st.free_mib} / {st.total_mib} Mio ({st.name})",
    ]
    procs = gpu_processes()
    heavy = [p for p in procs if p.used_mib > 0]
    if heavy:
        lines.append("Processus GPU actifs :")
        lines += [f"  - {p.name} (PID {p.pid}) : {p.used_mib} Mio" for p in heavy]
    elif procs:
        lines.append(f"{len(procs)} processus GPU actifs (consommation par processus non fournie par le pilote Windows)")
    if estimated_mib > st.free_mib:
        lines.append("Attention : VRAM libre insuffisante.")
    return "\n".join(lines)


if __name__ == "__main__":
    tool = sys.argv[1] if len(sys.argv) > 1 else "outil non précisé"
    est = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    print(approval_request(tool, est))

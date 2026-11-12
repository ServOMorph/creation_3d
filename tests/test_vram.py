import subprocess

from pipeline import vram


def _smi_free():
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, check=True).stdout
    total, free = [int(x) for x in out.splitlines()[0].split(",")]
    return total, free


def test_gpu_state_matches_nvidia_smi():
    st = vram.gpu_state()
    total, free = _smi_free()
    assert st.total_mib == total
    assert abs(st.free_mib - free) < 512
    assert st.used_mib + st.free_mib <= st.total_mib + 64


def test_processes_are_parsed():
    for p in vram.gpu_processes():
        assert p.pid > 0 and p.used_mib >= 0


def test_approval_flags_insufficient_vram():
    msg = vram.approval_request("test", 10**7)
    assert "insuffisante" in msg
    assert "VRAM libre" in msg

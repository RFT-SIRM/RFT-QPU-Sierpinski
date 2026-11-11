"""Generate the level-1 multi-tone qutrit resonance screen."""
import argparse,csv,json
from pathlib import Path
from rft_qpu.floquet_audit import audit_floquet_collisions

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--hardware-dir",type=Path,default=Path("hardware/level1"))
 p.add_argument("--output",type=Path,default=Path("results/floquet_collision_audit.json"))
 p.add_argument("--warning-window-MHz",type=float,default=10.0)
 a=p.parse_args()
 with (a.hardware_dir/"couplers.csv").open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
 report=audit_floquet_collisions(rows,warning_window_MHz=a.warning_window_MHz)
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2),encoding="utf-8")
 print(json.dumps({"output":str(a.output),**report["summary"]},indent=2))
if __name__=="__main__": main()

"""First-order Floquet collision screen for the level-1 multi-tone pump map."""
from __future__ import annotations
from collections import Counter
import math


def _alpha(mode: str, up: float, down: float) -> float:
    if mode.endswith("_up"): return up
    if mode.endswith("_dn"): return down
    raise ValueError(f"unknown mode: {mode}")


def audit_floquet_collisions(rows: list[dict], *, alpha_up_MHz: float=-250.0,
                             alpha_down_MHz: float=-245.0, warning_window_MHz: float=10.0,
                             harmonics: tuple[int,...]=(1,2,3),
                             include_intermodulation: bool=True) -> dict:
    """Compare pump sidebands with every exported N=1/N=2 qutrit channel.

    This is a resonance screen, not a Sambe/Floquet propagation or error estimate.
    """
    if not rows: raise ValueError("coupler rows must not be empty")
    if warning_window_MHz < 0 or not math.isfinite(warning_window_MHz):
        raise ValueError("warning window must be finite and non-negative")
    edges={}
    for row in rows:
        e=edges.setdefault(str(row["edge_id"]),{
            "id":str(row["edge_id"]),
            "frame":float(row["frame_detuning_MHz_signed"]),
            "onsite":float(row["target_onsite_detuning_MHz_signed"]),
            "pump":float(row["pump_frequency_MHz"]),"channels":[]})
        e["channels"].append(row)
    tones=[]
    ordered=list(edges.values())
    for e in ordered:
        for n in harmonics:
            if n<1: raise ValueError("harmonic orders must be positive")
            tones.append({"source":e["id"],"kind":"fundamental" if n==1 else f"harmonic_{n}",
                          "frequency":n*e["pump"],"assumption":"applied tone" if n==1 else "conditional nonlinear harmonic"})
    if include_intermodulation:
        for i,x in enumerate(ordered):
            for y in ordered[i+1:]:
                for kind,f in (("difference_product",abs(x["pump"]-y["pump"])),("sum_product",x["pump"]+y["pump"])):
                    if f>1e-12: tones.append({"source":x["id"]+"+"+y["id"],"kind":kind,"frequency":f,
                                              "assumption":"conditional nonlinear intermodulation"})
    hits=[]; min_primary=math.inf; min_all=math.inf; checks_primary=0; checks_all=0
    for tone in tones:
        primary=tone["kind"]=="fundamental"
        f=tone["frequency"]
        for victim in ordered:
            sidebands=(abs(victim["frame"]+f),abs(victim["frame"]-f))
            for ch in victim["channels"]:
                ma,mb=str(ch["mode_a"]),str(ch["mode_b"])
                aa=_alpha(ma,alpha_up_MHz,alpha_down_MHz)
                ab=_alpha(mb,alpha_up_MHz,alpha_down_MHz)
                transitions=(("N1_exchange",abs(victim["onsite"])),
                             ("N2_11_to_20",abs(victim["onsite"]+aa)),
                             ("N2_11_to_02",abs(victim["onsite"]-ab)),
                             ("N2_20_to_02",abs(2*victim["onsite"]+aa-ab)))
                for si,sb in enumerate(sidebands):
                    for label,ef in transitions:
                        if primary and tone["source"]==victim["id"] and sb<=1e-9:
                            if label=="N1_exchange" or (label=="N2_20_to_02" and ef<=1e-9): continue
                        margin=abs(sb-ef); checks_all+=1; min_all=min(min_all,margin)
                        if primary: checks_primary+=1; min_primary=min(min_primary,margin)
                        if margin<=warning_window_MHz:
                            hits.append({"source":tone["source"],"component":tone["kind"],
                              "component_assumption":tone["assumption"],"component_frequency_MHz":f,
                              "victim_edge":victim["id"],"victim_mode_a":ma,"victim_mode_b":mb,
                              "rotating_sideband_MHz":sb,"sideband_sign":"+" if si==0 else "-",
                              "transition":label,"transition_frequency_MHz":ef,"collision_margin_MHz":margin})
    hits.sort(key=lambda x:(x["collision_margin_MHz"],x["source"],x["victim_edge"]))
    primary_hits=[x for x in hits if x["component"]=="fundamental"]
    return {"model":"first-order multi-tone Floquet resonance screen","is_full_floquet_solution":False,
      "is_transition_probability":False,
      "input":{"edge_count":len(edges),"effective_channel_count":len(rows),
       "primary_pump_count":len({e["pump"] for e in ordered}),"alpha_up_MHz":alpha_up_MHz,
       "alpha_down_MHz":alpha_down_MHz,"harmonics_included":list(harmonics),
       "pairwise_intermodulation_included":include_intermodulation,"warning_window_MHz":warning_window_MHz},
      "summary":{"primary_component_minimum_margin_MHz":None if math.isinf(min_primary) else min_primary,
       "all_component_minimum_margin_MHz":None if math.isinf(min_all) else min_all,
       "primary_component_warning_count":len(primary_hits),"all_component_warning_count":len(hits),
       "warnings_by_component":dict(Counter(x["component"] for x in hits)),
       "checks_primary":checks_primary,"checks_all":checks_all},
      "worst_primary_collisions":primary_hits[:100],"worst_all_collisions":hits[:100],
      "interpretation":"Possible resonance only if the source tone reaches the victim path. No measured transfer functions or transition probabilities are represented."}

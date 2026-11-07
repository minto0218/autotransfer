"""Prove the last hook-access refinement only removes rigid material.
Full pose tests are retained as the baseline, without pretending to rerun them.
"""
import json,importlib.util,hashlib
import build as b
import prototype
base={};apply=prototype.apply
def capture(bb):
 base.update(parts=dict(bb.PARTS),meta={n:dict(m)for n,m in bb.META.items()});apply(bb)
prototype.apply=capture
b.make_parts();new=b.PARTS['spring_cassette']
spec=importlib.util.spec_from_file_location('old_hook',str(b.OUT/'validation/baseline_prototype_before_hook.py'));old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
b.PARTS.clear();b.PARTS.update(base['parts']);b.META.clear();b.META.update(base['meta']);old.apply(b);before=b.PARTS['spring_cassette']
added=abs(new.cut(before).Volume());removed=abs(before.cut(new).Volume());rep=dict(changed_part='spring_cassette',added_material_mm3=added,removed_material_mm3=removed,also_removed_instances='spring_tendon_eye x3 per head; string ties directly to metal spring hook',claim='If baseline rigid contacts are zero, subtracting this material and removing the three eyelets cannot create a rigid contact in any pose.',subset_pass=added<1e-6)
(b.OUT/'validation/hook_clearance_delta.json').write_text(json.dumps(rep,indent=2));print(rep,flush=True)

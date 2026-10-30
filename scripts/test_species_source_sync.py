#!/usr/bin/env python3
"""Isolated tests for site species update: new, existing, reject wrong family."""
import importlib.util,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("new_sync",ROOT/"scripts/sync_source_species_to_site.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def main():
    with tempfile.TemporaryDirectory(prefix="hays-source-sync-") as d:
        root=Path(d);source=root/"source";site=root/"site"
        shutil.copytree(ROOT/"site/data",site/"data")
        record="content/taxa/Apocynaceae/Amsonia/amsonia-new-test-record/species.json"
        p=source/record;p.parent.mkdir(parents=True)
        payload={"id":"amsonia-new-test-record","family":"Apocynaceae","genus":"Amsonia",
                 "scientific_name":"Amsonia synthetic-test","common_name":"Synthetic CI only",
                 "look_here_first":"Synthetic source record, NOT a real botanical claim.",
                 "morphology_keys":{"best_field_traits":["No real plant depicted"]}}
        p.write_text(json.dumps(payload))
        before=json.loads((site/"data/collection-index.json").read_text())
        out=module.render(source,site,[record],check=True)
        assert out["new_species"]==1
        assert not (site/"data/species/amsonia-new-test-record.json").exists()
        out=module.render(source,site,[record],check=False)
        assert out["new_species"]==1
        assert json.loads((site/"data/collection-index.json").read_text())["entries"][-1]["id"]==payload["id"]
        assert (site/"data/species/amsonia-new-test-record.json").is_file()
        orig=(site/"data/species/amsonia-ciliata.json")
        prior=json.loads(orig.read_text())
        assert prior.get("verified_photos")
        old="content/taxa/Apocynaceae/Amsonia/amsonia-ciliata/species.json"
        f=source/old;f.parent.mkdir(parents=True,exist_ok=True)
        oldraw={"id":"amsonia-ciliata","family":"Apocynaceae","genus":"Amsonia",
                 "scientific_name":"Amsonia ciliata","common_name":"Fringed bluestar (new)",
                 "look_here_first":"Improved automatic text without changing approved photos",
                 "morphology_keys":{"best_field_traits":["Narrow foliage"]}}
        f.write_text(json.dumps(oldraw))
        module.render(source,site,[old])
        after=json.loads(orig.read_text())
        assert after["verified_photos"]==prior["verified_photos"]
        assert after["common_name"]=="Fringed bluestar (new)"
        payload["family"]="Poaceae";p.write_text(json.dumps(payload))
        try:module.render(source,site,[record])
        except ValueError:pass
        else:raise AssertionError("Wrong family should have been rejected")
        assert len(before["entries"])+1==len(json.loads((site/"data/collection-index.json").read_text())["entries"])
    print("PASS: new family species, verified photo preservation, scoped edits, wrong-family rejection")
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Recovery batch: seven named, attributed CC BY 4.0 Solanum journal figure panels.

Each figure crop is already archived in original staging and separately credited
to the photographer in the per-photo historical source CSV. The source article
(Knapp et al. 2019 PhytoKeys 123 DOI 10.3897/phytokeys.123.31738) explicitly
grants CC BY 4.0. Never republish holds or guess a grant.
"""
import csv, hashlib, json, pathlib, sys
from collections import Counter

archive=pathlib.Path(sys.argv[1])
site=pathlib.Path("site")
indexpath=site/"data/collection-index.json"
gallerypath=site/"data/gallery-index.json"
index=json.loads(indexpath.read_text())
gallery=json.loads(gallerypath.read_text())
byid={r["id"]:r for r in index["entries"]}
spec={
 "solanum-emulans":[
   ("04-leaf-underside-figure16b.jpg","d6370b514f588e66bf198e730025e7a16ff8ec0c","116"),
   ("05-flower-anthers-figure16c.jpg","4fe36842f25ba9fb6e955e099192b0d1e064cca7","116"),
   ("06-developing-green-fruit-calyx-figure16d.jpg","06cb8ba9551e8b71ebcc19202b747216d00c22f8","116")],
 "solanum-interius":[
   ("01-habit-figure22a.jpg","0e4a1297811ecfbca6106631aa1ffe690741df12","122"),
   ("02-flower-branches-figure22b.jpg","4c294b912df0e14b90b918ac99a72be1fefe9822","122"),
   ("03-developing-fruit-calyx-figure22c.jpg","8c93cf1f0a8779da0de7cdf83b2c4485f70b2cc5","122"),
   ("04-ripe-black-fruit-figure22d.jpg","005749f911a65aada84f064111156784323de20b","122")]
}
def gitsha(raw):
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
if sum(r["photo_count"] for r in index["entries"])!=gallery["photo_count"]:
 raise RuntimeError("preexisting gallery count conflict")
if any(gallery["entries"][slug]["count"]!=r["photo_count"] for slug,r in byid.items()):
 raise RuntimeError("preexisting per-species count conflict")
added=Counter()
for slug,items in spec.items():
 folder=archive/"content/taxa/Solanaceae/Solanum"/slug
 if not (folder/"image-sources.csv").is_file():raise RuntimeError("Source CSV missing "+slug)
 with (folder/"image-sources.csv").open(newline="",encoding="utf-8-sig") as f:
  rows={pathlib.Path(r["file"]).name:r for r in csv.DictReader(f) if r.get("file")}
 path=site/"data/species"/(slug+".json")
 card=json.loads(path.read_text())
 if card["scientific_name"]!="Solanum "+slug.split("-",1)[1]:raise RuntimeError("taxon mismatch "+slug)
 if len(card["verified_photos"])!=byid[slug]["photo_count"]:raise RuntimeError("card/index conflict")
 for name,sha,figure in items:
  if name not in rows:raise RuntimeError("missing exact source metadata "+name)
  row=rows[name]
  page="https://phytokeys.pensoft.net/article/31738/element/2/"+figure+"/"
  if (row.get("license")!="CC BY 4.0" or row.get("license_url")!="https://creativecommons.org/licenses/by/4.0/"
      or row.get("source_page")!=page or "2019" not in row.get("creator","") and not row.get("creator")):
   raise RuntimeError("source figure/rights inconsistent "+name)
  if row.get("creator") not in ("Michael Nee","Tiina Särkinen","Michael Nee (photograph); Knapp et al. (2019, Figure 16 layout)"):
   raise RuntimeError("unrecognized figure photographer "+name)
  original=archive/"migration/private-original-photo-holds/Solanaceae/Solanum"/slug/"images"/name
  raw=original.read_bytes()
  if gitsha(raw)!=sha or not raw.startswith(b"\xff\xd8\xff"):
   raise RuntimeError("original source bytes inconsistent "+name)
  if any(p.get("source_blob_sha")==sha for p in card["verified_photos"]):
   print("ALREADY_VISIBLE",slug,name,flush=True)
   continue
  dest="media/"+slug+"/historical-phytokeys-"+sha[:16]+".jpg"
  if (site/dest).exists():raise RuntimeError("unindexed destination "+dest)
  (site/dest).parent.mkdir(parents=True,exist_ok=True)
  (site/dest).write_bytes(raw)
  card["verified_photos"].append({
    "src":dest,"creator":row["creator"],"source_page":page,
    "source_page_is_exact":True,"license":"CC BY 4.0",
    "license_url":"https://creativecommons.org/licenses/by/4.0/",
    "source_blob_sha":sha,"role":row["role"],
    "modified":row.get("modifications") or "Original publication figure panel reproduced from historical archive",
    "noncommercial_only":False,"private_rights_review_only":False,
    "photo_approval_mode":"OWNER_STANDING_PHOTO_FIRST_POLICY",
    "photo_approved_by":"Source figure, photographed author, 2019 PhytoKeys article CC BY 4.0, and original Git image hash verified",
    "source_review_evidence":"Knapp et al. 2019 CC BY 4.0, DOI https://doi.org/10.3897/phytokeys.123.31738; exact figure "+figure+"; historical photo sha "+sha+"; named figure photographer "+row["creator"],
    "taxon_review_evidence":"Figure panels from the scholarly treatment of Solanum "+slug.split("-",1)[1]+"; original labeled A/B/C/D panels visibly inspected; advanced annotations deferred"
  })
  added[slug]+=1
  print("PUBLISH_READY",slug,name,sha,flush=True)
 if added[slug]:
  path.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
  byid[slug]["photo_count"]+=added[slug]
  gallery["entries"][slug]["count"]+=added[slug]
if added:
 gallery["photo_count"]+=sum(added.values())
 indexpath.write_text(json.dumps(index,indent=2,ensure_ascii=False)+"\n")
 gallerypath.write_text(json.dumps(gallery,indent=2,ensure_ascii=False)+"\n")
assert sum(r["photo_count"] for r in index["entries"])==gallery["photo_count"]
assert all(byid[k]["photo_count"]==v["count"] for k,v in gallery["entries"].items())
print("ASTEROID_PHYTO_KEYS_BATCH",json.dumps({"installed":sum(added.values()),"by_species":dict(added),"gallery_count":gallery["photo_count"]}),flush=True)

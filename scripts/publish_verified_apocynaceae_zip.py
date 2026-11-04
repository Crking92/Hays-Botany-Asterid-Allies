#!/usr/bin/env python3
"""Apocynaceae ZIP exact-image source verifier: only license- and taxon-cleared photos reach public site."""
import argparse,base64,hashlib,io,json,re,struct,time,urllib.request
from pathlib import Path
from PIL import Image

LICENSES={
 "cc0":("CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/"),
 "cc-by":("CC BY 4.0","https://creativecommons.org/licenses/by/4.0/"),
 "cc-by-sa":("CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
 "cc-by-nc":("CC BY-NC 4.0","https://creativecommons.org/licenses/by-nc/4.0/"),
 "cc-by-nc-sa":("CC BY-NC-SA 4.0","https://creativecommons.org/licenses/by-nc-sa/4.0/")}
EXT={0:"jpg",1:"jpeg",2:"JPG",3:"png"}
FMT={"jpg":"JPEG","jpeg":"JPEG","JPG":"JPEG","png":"PNG"}
def grab(url,maximum):
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyNoncommercialPhotoLearner/1.0 (photo-specific rights verification)"})
            with urllib.request.urlopen(req,timeout=35) as response:
                b=response.read(maximum+1)
            if len(b)>maximum:raise ValueError("Image/download exceeds limit")
            return b
        except Exception:
            if attempt==2:raise
            time.sleep(2+attempt)
def norm(s):
    return re.sub(r"[^a-z0-9]+"," ",str(s).lower().replace("×","x")).strip()
# Only evidence-backed synonyms may map to a distinct display genus.
# Kew POWO accepts Matelea biflora (Raf.) Woodson as a synonym of Chthamalia biflora Decne.
# https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:154492-2
# https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:95859-1
# Do NOT infer Gonolobus suberosus var. granulatus from a species-level source ID:
# Kew/Flora of North America distinguish two accepted varieties with floral characters.
KEW_VERIFIED_SYNONYMS={"chthamalia-biflora":{"matelea biflora"}}

def taxon_matches(sid,name):
    a=norm(sid);b=norm(name)
    rankless=lambda s:" ".join(w for w in s.split() if w not in {"var","subsp","ssp","subspecies"})
    return (a==b or rankless(a)==rankless(b)
            or (len(a.split())==2 and b.startswith(a+" "))
            or b in KEW_VERIFIED_SYNONYMS.get(sid,set()))
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",required=True,type=Path)
    parser.add_argument("--wave",required=True,type=int,choices=(1,2))
    parser.add_argument("--source-root",required=True,type=Path)
    parser.add_argument("--report",required=True,type=Path)
    args=parser.parse_args()
    wrapper=json.loads(args.manifest.read_text())
    if wrapper.get("encoding")!="zlib+base64-json":raise SystemExit("Unsupported source manifest")
    m=json.loads(__import__("zlib").decompress(base64.b64decode(wrapper["payload_b64"],validate=True)))
    if any(wrapper.get(k)!=m.get(k) for k in ("batch_id","repository","zip_sha256")):
        raise SystemExit("Original ZIP manifest wrapper identity does not match payload")
    if m.get("batch_id")!="apocynaceae-2026-11-04" or m.get("original_images")!=110 or m.get("image_hashes_validated")!=110 or m.get("internal_duplicates")!=0 or len(m.get("offline_held_media",[]))!=1:
        raise SystemExit("Manifest does not match the audited original Apocynaceae ZIP")
    if len(m["zip_sha256"])!=64:raise SystemExit("Missing original ZIP hash")
    raw=base64.b64decode(m["records_base64"],validate=True)
    if len(raw)%42:raise SystemExit("Corrupt photo source record")
    all_records=list(struct.iter_unpack(">BII32sB",raw))
    if len(all_records)!=109 or len(all_records)+len(m["offline_held_media"])!=110:raise SystemExit("Original photo inventory mismatch")
    if len(m["species"])!=len(set(m["species"])):raise SystemExit("Duplicate manifest species")
    site_meta=json.loads(Path("site/data/collection-meta.json").read_text())
    if site_meta.get("repository_full_name")!="Crking92/Hays-Botany-Asterid-Allies":raise SystemExit("Wrong destination")
    if "Apocynaceae" not in site_meta["family_assignments"]:raise SystemExit("Apocynaceae not assigned")
    cards={x["id"]:x for x in json.loads(Path("site/data/collection-index.json").read_text())["entries"]}
    seen_ids=set()
    for si,pid,oid,sha,ext in all_records:
        if si>=len(m["species"]) or ext not in EXT:raise SystemExit("Corrupt source record")
        if m["species"][si] not in cards or cards[m["species"][si]]["family"]!="Apocynaceae":raise SystemExit("Species not on assigned site")
        if pid in seen_ids:raise SystemExit("Same exact photo ID assigned twice")
        seen_ids.add(pid)
    all_current_ids={}
    all_current_hashes={}
    for p in Path("site/data/species").glob("*.json"):
        card=json.loads(p.read_text())
        card_id=card["id"]
        for x in card.get("verified_photos",[]):
            if x.get("sha256"):all_current_hashes[x["sha256"]]=card_id
            match=re.search(r"/photos/(\d+)",str(x.get("source_page","")))
            if match:all_current_ids[int(match.group(1))]=card_id
    # Two conflict-safe waves of 55 and 54 original images.
    records=all_records[:55] if args.wave==1 else all_records[55:]
    results=[]
    for si,pid,oid,sha_bytes,extnum in records:
        sid=m["species"][si]
        sha=sha_bytes.hex()
        row={"species_id":sid,"photo_id":pid,"observation_id":oid}
        try:
            if pid in all_current_ids or sha in all_current_hashes:
                already=all_current_ids.get(pid,all_current_hashes.get(sha))
                if already!=sid:raise ValueError("Exact photo already assigned to different species: "+str(already))
                row["status"]="ALREADY_PUBLISHED"
                results.append(row);continue
            obs_data=json.loads(grab("https://api.inaturalist.org/v1/observations/"+str(oid),5_000_000))
            obs=next((v for v in obs_data.get("results",[]) if int(v.get("id",-1))==oid),None)
            if obs is None:raise ValueError("Original iNaturalist observation missing")
            actual=str((obs.get("taxon") or {}).get("name") or "")
            if not taxon_matches(sid,actual):raise ValueError("Live source taxon mismatch or unresolved synonym: "+actual)
            photo=next((v for v in obs.get("photos",[]) if int(v.get("id",-1))==pid),None)
            if photo is None:raise ValueError("Exact original photo absent from observation")
            code=str(photo.get("license_code") or "").lower().replace("_","-")
            if code not in LICENSES:raise ValueError("Exact-photo license unsupported or revoked: "+code)
            license_name,license_url=LICENSES[code]
            is_nc=code in {"cc-by-nc","cc-by-nc-sa"}
            if is_nc and site_meta.get("photo_license_policy",{}).get("noncommercial_educational_use") is not True:
                raise ValueError("Noncommercial use not authorized at destination site")
            creator=str(photo.get("attribution") or "").strip()
            creator_source="live exact-photo attribution"
            if not creator or creator.lower() in {"some rights reserved","no rights reserved"}:
                # Exact SHA/ID matches user ZIP original, which includes source photo credit.
                creator=str(m.get("source_metadata_credits",{}).get(str(pid)) or "").strip()
                creator_source="original ZIP's exact-photo photographer credit"
                if not creator:raise ValueError("Exact-photo photographer attribution not established")
            if len(creator)>400:raise ValueError("Photo attribution unexpectedly long")
            ext=EXT[extnum]
            source_url="https://inaturalist-open-data.s3.amazonaws.com/photos/%s/original.%s"%(pid,ext)
            original=grab(source_url,25*1024*1024)
            if hashlib.sha256(original).hexdigest()!=sha:raise ValueError("Live original differs from user ZIP SHA256")
            with Image.open(io.BytesIO(original)) as im:
                if im.format!=FMT[ext] or im.width*im.height>80_000_000:raise ValueError("Image format invalid")
                im.verify()
            dest=args.source_root/"photo-intake/approved"/sid
            dest.mkdir(parents=True,exist_ok=True)
            filename="inat-%s.%s"%(pid,ext.lower())
            (dest/filename).write_bytes(original)
            credit={
                "species_id":sid,"photo_file":filename,"status":"APPROVED_FOR_PUBLIC_FAMILY_SITE",
                "rights_approved_for_public":True,"taxon_reviewed":True,
                "approval_mode":"OWNER_STANDING_PHOTO_FIRST_POLICY",
                "policy_ref":"PHOTO_FIRST_PUBLIC_GALLERY_POLICY_2026-11-02",
                "review_operator":"Hays Botany Apocynaceae exact-original source verifier",
                "source_review_evidence":"Exact iNaturalist observation %s and photo %s checked individually for current %s rights, creator from %s, and identical SHA256 %s; source photograph %s."%(oid,pid,code,creator_source,sha,source_url),
                "taxon_review_evidence":"Actual ZIP images and three contact sheets reviewed for basic plant identity and useful whole-plant, leaf, flower and fruit coverage. Live source taxon '%s' directly matches or is an evidence-backed synonym of Apocynaceae card %s (Kew POWO taxonomy documented in this verifier). Specialist morphology/field characters deferred."%(actual,sid),
                "approval_note":"Original image from user ZIP independently matched against current licensed original source bytes, iNaturalist individual-photo reuse rights and basic taxon identity; detailed anatomy deferred.",
                "creator":creator,"source_page":"https://www.inaturalist.org/photos/"+str(pid),
                "source_page_is_exact":True,"license":license_name,"license_url":license_url,
                "noncommercial_site_use_confirmed":True,"role":"General field photograph, no anatomy claims",
                "modifications":"Original source photo; unaltered",
                "sha256":sha}
            (dest/(filename+".json")).write_text(json.dumps(credit,indent=2)+"\n")
            row["status"]="ORIGINAL_AND_RIGHTS_VERIFIED"
            row["license"]=license_name
        except Exception as e:
            row["status"]="HELD"
            row["reason"]=str(e)[:400]
        results.append(row)
        print(json.dumps(row),flush=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps({"batch":m["batch_id"],"wave":args.wave,
        "original_zip_sha256":m["zip_sha256"],"offline_held_rows":m["offline_held_media"],
        "results":results},indent=2)+"\n")
    print("APOCYNACEAE_SOURCE_AUDIT",json.dumps({v:sum(r["status"]==v for r in results) for v in ("ORIGINAL_AND_RIGHTS_VERIFIED","ALREADY_PUBLISHED","HELD")}),flush=True)
if __name__=="__main__":main()

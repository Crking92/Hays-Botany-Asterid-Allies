#!/usr/bin/env python3
import json,urllib.request,time
for oid in (5110303867,5110327660,5110335993,5110543645):
    url="https://api.gbif.org/v1/occurrence/"+str(oid)
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyGBIFSourceRightsCheck/1.0","Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=25) as resp:d=json.load(resp)
        print("GBIF_PHOTO_RIGHTS_EVIDENCE",json.dumps({
            "id":oid,"species":d.get("species"),"datasetKey":d.get("datasetKey"),
            "datasetName":d.get("datasetName"),"publishingOrgKey":d.get("publishingOrgKey"),
            "license":d.get("license"),"references":d.get("references"),
            "rightsHolder":d.get("rightsHolder"),
            "media":d.get("media",[])[:2],
        },ensure_ascii=False),flush=True)
    except Exception as e:
        print("GBIF_PROBE_HOLD",oid,str(e)[:210],flush=True)
    time.sleep(.5)

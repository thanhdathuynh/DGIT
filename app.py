from flask import Flask, request, render_template
import requests

app = Flask(__name__)
DGIDB_API_URL = "https://dgidb.org/api/graphql"
#API for genome info (maybe ucsc genome browser)

MDD_GENES = [
    "SLC6A4",
    "BDNF",
    "HTR2A",
    "TPH2",
    "GNB3",
    "MTHFR",
    "DRD2",
    "CELF4",
    "LAMB2",
    "FKBP5"
]

MDD_PROTEINS = [
    "BDNF",
    "IL-6",
    "CRP",
    "TNF‑α",
    "ITIH4",
    "CD155",
    "Lipocalin-2",
    "HGF",
    "LIGHT",
    "C1QC",
]

MDD_DRUGS = [
    "Fluoxetine",
    "Sertraline",
    "Venlafaxine",
    "Levomilnacipran",
    "Citalopram",
    "Escitalopram",
    "Milnacipran",
    "Trazodone",
    "Mirtazapine",
    "Vortioxetine",
]

GENE_ALIASES = {
    "5-HT2A": "HTR2A",
    "5HT2A": "HTR2A",
    "SEROTONIN RECEPTOR 2A": "HTR2A",
    "SEROTONIN TRANSPORTER": "SLC6A4",
    "SERT": "SLC6A4",
    "BRAIN-DERIVED NEUROTROPHIC FACTOR": "BDNF",
    "TRYPTOPHAN HYDROXYLASE 2": "TPH2",
    "DOPAMINE RECEPTOR D2": "DRD2",
    "FK506 BINDING PROTEIN 5": "FKBP5",
    "METHYLENETETRAHYDROFOLATE REDUCTASE": "MTHFR",
    "G PROTEIN BETA 3": "GNB3",
}

DRUG_ALIASES = {
    "PROZAC": "Fluoxetine",
    "ZOLOFT": "Sertraline",
    "CELEXA": "Citalopram",
    "LEXAPRO": "Escitalopram",
    "EFFEXOR": "Venlafaxine",
    "SAVELLA": "Milnacipran",
    "REMERON": "Mirtazapine",
    "TRINTELLIX": "Vortioxetine",
    #we can add more brands if anything
}

PROTEIN_ALIASES = {
    "IL-6": "IL6", "IL6": "IL6", "CRP": "CRP",
    "TNF": "TNF", "TNF-ALPHA": "TNF", "TNF-ΑLPHA": "TNF",  
    "TNF-α": "TNF","TNF-Α": "TNF", "TNF-α": "TNF",       
    "ITIH4": "ITIH4", "CD155": "PVR","LIPOCALIN-2": "LCN2",
    "LIPOCALIN 2": "LCN2","HGF": "HGF","LIGHT": "TNFSF14",
    "C1QC": "C1QC","BDNF": "BDNF",
}


#for parsing the gene results that way we can easily put it in table form
def parseGeneResults(json_data):
    rows = []
    nodes = (json_data.get("data",{}).get('genes',{}) or {}).get('nodes',[]) or []
    for n in nodes:
        for it in n.get("interactions", []) or []:
            drug = it.get("drug") or {}
            types = ", ".join([t.get("type","") for t in (it.get("interactionTypes") or []) if t.get("type")]) or "—"
            dirs  = ", ".join([t.get("directionality","") for t in (it.get("interactionTypes") or []) if t.get("directionality")]) or "—"
            sources = ", ".join([s.get("sourceDbName","") for s in (it.get("sources") or []) if s.get("sourceDbName")]) or "—"
            pmids = ", ".join([str(p.get("pmid")) for p in (it.get("publications") or []) if p.get("pmid")]) or "—"
            rows.append({
                "left_label": "Gene",
                "left_name": n.get("name") or "",
                "left_cid": n.get("conceptId") or "",
                "right_label": "Drug",
                "right_name": drug.get("name") or "",
                "right_cid": drug.get("conceptId") or "",
                "types": types, "directions": dirs, "score": it.get("interactionScore"),
                "sources": sources, "pmids": pmids
            })
    return rows

def parseProteinResults(json_data):
    rows = []
    if not json_data:
        return rows
    for hit in json_data.get("results", []):
        protein_name = None
        description = None
        #protein description
        if hit.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}):
            description = hit["proteinDescription"]["recommendedName"]["fullName"].get("value")
        #protein name
        if hit.get("proteinDescription", {}).get("recommendedName", {}).get("shortNames"):
            sn = hit["proteinDescription"]["recommendedName"]["shortNames"]
            if sn and isinstance(sn, list) and sn[0].get("value"):
                protein_name = sn[0]["value"]

        uniprot_id = hit.get("primaryAccession")
        organism = hit.get("organism", {}).get("scientificName")

        gene_symbols = []
        for g in hit.get("genes", []):
            if g.get("geneName", {}).get("value"):
                gene_symbols.append(g["geneName"]["value"])
            for syn in g.get("synonyms", []):
                if syn.get("value"):
                    gene_symbols.append(syn["value"])

        rows.append({
            "protein_name": protein_name,
            "description": description,
            "uniprot_id": uniprot_id,
            "organism": organism,
            "genes": ", ".join(gene_symbols) if gene_symbols else "—"
        })
    return rows

#for parsing the gene results that way we can easily put it in table form
def parseDrugResults(json_data):
    rows = []
    nodes = (json_data.get("data", {}).get("drugs", {}) or {}).get("nodes", []) or []
    for n in nodes:
        for it in n.get("interactions", []) or []:
            gene = it.get("gene") or {}
            types = ", ".join([t.get("type","") for t in (it.get("interactionTypes") or []) if t.get("type")]) or "—"
            dirs  = ", ".join([t.get("directionality","") for t in (it.get("interactionTypes") or []) if t.get("directionality")]) or "—"
            sources = ", ".join([s.get("sourceDbName","") for s in (it.get("sources") or []) if s.get("sourceDbName")]) or "—"
            pmids = ", ".join([str(p.get("pmid")) for p in (it.get("publications") or []) if p.get("pmid")]) or "—"
            rows.append({
                "left_label": "Drug",
                "left_name": n.get("name") or "",
                "left_cid": n.get("conceptId") or "",
                "right_label": "Gene",
                "right_name": gene.get("longName") or gene.get("name") or "",
                "right_cid": gene.get("conceptId") or "",
                "types": types, "directions": dirs, "score": it.get("interactionScore"),
                "sources": sources, "pmids": pmids
            })
    return rows

#this is for normalizing the user search so it works with dgidb, basically lets you search by brand, genes
def normalize_term(search_type: str, s: str) -> str:
    if not s:
        return s
    key = s.strip().upper()
    if search_type == "gene":
        return GENE_ALIASES.get(key, s.strip().upper())
    elif search_type == "protein": 
        return PROTEIN_ALIASES.get(key, key)
        
    else:
        #maps the drug brands to the generic name
        drug = DRUG_ALIASES.get(key)
        return drug if drug else s.strip().title()
    
def fetchProteinResults(protein_name: str):
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"({protein_name}) AND organism_id:9606",  # 9606 = human
        # 'genes' is NOT a valid field name; use these instead:
        "fields": "accession,protein_name,gene_primary,gene_names,organism_name",
        "format": "json",
        "size": 5
    }
    headers = {
        "User-Agent": "DGIT",
        "Accept": "application/json"
    }
    resp = None
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        print("UniProt URL:", resp.url)
        resp.raise_for_status()
        return resp.json(), None
    except requests.HTTPError as e:
        status = resp.status_code if resp is not None else "unknown"
        body_snip = (resp.text or "")[:300] if resp is not None else ""
        return None, f"UniProt HTTP error {status} at {(resp.url if resp else url)}: {e}. Body: {body_snip}"
    except requests.RequestException as e:
        return None, f"UniProt request failed: {e}"


@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    error = None
    mdd_list = None

    rows = []
    search_type = None
    query_value = ""

    if request.method == 'POST':
        search_type = request.form.get('type')
        query_value = request.form.get('query', '').strip()
        query_value = normalize_term(search_type, query_value)
        if not search_type:
            error = "Please select a type."
        else:
            if query_value == '':
                # Show full MDD list if query empty
                if search_type == 'gene':
                    mdd_list = MDD_GENES
                  
                elif search_type == "protein":
                    mdd_list = MDD_PROTEINS
                elif search_type == 'drug':
                    mdd_list = MDD_DRUGS
                else:
                    error = "Invalid type selected."
            else:
                # Query DGIdb API if input is not empty
                if search_type == 'gene': #search interaction by gene
                    query = """
                    query($names: [String!]!) {
                      genes(names: $names) {
                        nodes {
                          interactions {
                            drug {
                              name
                              conceptId
                            }
                            interactionScore
                            interactionTypes {
                              type
                              directionality
                            }
                            interactionAttributes {
                              name
                              value
                            }
                            publications {
                              pmid
                            }
                            sources {
                              sourceDbName
                            }
                          }
                        }
                      }
                    }
                    """

                    variables = {"names": [query_value]}
                    try:
                        response = requests.post(DGIDB_API_URL, json={"query": query, "variables": variables}, timeout=20)
                        response.raise_for_status()
                        results = response.json()
                        if not results.get("errors"):
                            rows = parseGeneResults(results)
                        else:
                            error = results["errors"][0].get("message", "GraphQL error")
                    except requests.RequestException as e:
                        error = f"Failed to query DGIdb API: {e}"

                elif search_type == 'protein':
                  try:
                      protein_json, uni_err = fetchProteinResults(query_value)
                      if uni_err:
                          error = uni_err
                      else:
                          results = protein_json
                          rows = parseProteinResults(protein_json)
                  except Exception as e:
                      error = f"Failed to query UniProt: {e}"

                else:  # search interaction by gene
                    query = """
                    query($names: [String!]!) {
                      drugs(names: $names) {
                        nodes {
                          interactions {
                            gene {
                              name
                              conceptId
                              longName
                            }
                            interactionScore
                            interactionTypes {
                              type
                              directionality
                            }
                            interactionAttributes {
                              name
                              value
                            }
                            publications {
                              pmid
                            }
                            sources {
                              sourceDbName
                            }
                          }
                        }
                      }
                    }
                    """
                    variables = {"names": [query_value]}
                
                    try:
                        response = requests.post(DGIDB_API_URL, json={"query": query, "variables": variables}, timeout=20)
                        response.raise_for_status()
                        results = response.json()

                        if not results.get("errors"):
                            rows = parseGeneResults(results) if search_type == "gene" else parseDrugResults(results)
                        else:
                            error = results["errors"][0].get("message", "GraphQL error")
                    except requests.RequestException as e:
                        error = f"Failed to query DGIdb API: {str(e)}"

    return render_template('index.html',
                       results=results,
                       rows=rows,
                       search_type=search_type,
                       mdd_list=mdd_list,
                       error=error)


@app.route('/nav', methods=['GET'])
def nav():
  if request.method == 'GET':
      return render_template('nav.html')
  return render_template('nav.html')

if __name__ == '__main__':
    app.run(debug=True)

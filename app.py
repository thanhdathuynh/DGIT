from flask import Flask, request, render_template
import requests

app = Flask(__name__)
DGIDB_API_URL = "https://dgidb.org/api/graphql"
#API for genome info (maybe ucsc genome browser)
#API for protein info (maybe ncbi)

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
  nodes = (json_data.get("data",{}).get('genes',{}) or {}).get('nodes',[]) or []
    

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
        protein = PROTEIN_ALIASES.get(key)
        return protein if protein else s.strip().title()
    
    else:
        #maps the drug brands to the generic name
        drug = DRUG_ALIASES.get(key)
        return drug if drug else s.strip().title()
    


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

    return render_template('index.html', results=results, error=error, mdd_list=mdd_list, search_type=search_type, 
                           query=query_value,rows=rows)

if __name__ == '__main__':
    app.run(debug=True)

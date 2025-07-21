from flask import Flask, request, render_template
import requests

app = Flask(__name__)
DGIDB_API_URL = "https://dgidb.org/api/graphql"

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

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    error = None
    mdd_list = None

    if request.method == 'POST':
        search_type = request.form.get('type')
        query_value = request.form.get('query', '').strip()

        if not search_type:
            error = "Please select a type."
        else:
            if query_value == '':
                # Show full MDD list if query empty
                if search_type == 'gene':
                    mdd_list = MDD_GENES
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
                    response = requests.post(DGIDB_API_URL, json={"query": query, "variables": variables})
                    response.raise_for_status()
                    results = response.json()
                except requests.RequestException as e:
                    error = f"Failed to query DGIdb API: {str(e)}"

    return render_template('index.html', results=results, error=error, mdd_list=mdd_list)

if __name__ == '__main__':
    app.run(debug=True)
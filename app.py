from flask import Flask, request, render_template
import requests

app = Flask(__name__)
DGIDB_API_URL = "https://dgidb.org/api/graphql"

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    error = None

    if request.method == 'POST':
        search_type = request.form.get('type')
        query_value = request.form.get('query')

        if not search_type or not query_value:
            error = "Please select a type and enter a query."
        elif search_type not in ['gene', 'drug']:
            error = "Type must be 'gene' or 'drug'."
        else:
            if search_type == 'gene':
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
            else:  # drug
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

    return render_template('index.html', results=results, error=error)

if __name__ == '__main__':
    app.run(debug=True)
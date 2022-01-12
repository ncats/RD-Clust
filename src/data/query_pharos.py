from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import json
import csv
from pathlib import Path



def main():
    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url="https://pharos-api.ncats.io/graphql")

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True,execute_timeout=None)

    ligand_query_string = """
        query downloadQuery {{
  download(
    model: "Targets"
    fields: [
      "UniProt"
      "Symbol"
      "Ligand Name"
      "Ligand Is Drug"
      "Ligand SMILES"
      "Ligand PubChem ID"
      "Ligand ChEMBL ID"
      "Ligand DrugCentral ID"
      "Ligand PubMed IDs"
      "Preferred Term"
      "UNII"
    ]
    sqlOnly: false
    top:  {0}
    skip: {1}
    filter: {{
      facets: [
        {{ facet: "Target Development Level", values: ["Tchem","Tclin"], upSets: [] }}
      ]
    }}
  ) {{
    result
    data
  }}
}}
    """    

    disease_query_string = """
        query downloadQuery {{
  download(
    model: "Targets"
    fields: [
      "UniProt"
      "Symbol"
      "Disease Data Source"
      "Associated Disease Source"
      "Associated Disease Source ID"
      "Associated Disease Drug Name"
      "Linked Disease"
    ]
    sqlOnly: false
    top:  {0}
    skip: {1}
  ) {{
    result
    data
  }}
}}
    """      
    
    project_dir = Path(__file__).resolve().parents[2]
    
    #Target-Ligand data
    skip = 0
    ligand_res = []
    while True:
        res = client.execute(gql(ligand_query_string.format(100000,skip)))
        if len(res['download']['data'])>0:
            ligand_res.extend(res['download']['data'])
            skip +=100000
        else:
            break

    ligand_file = open(project_dir / 'data/raw/pharos_all_target_ligands.csv', "w")
    ligand_writer = csv.DictWriter(
       ligand_file,fieldnames=ligand_res[0].keys()
    )
    ligand_writer.writeheader()
    ligand_writer.writerows(ligand_res)
    ligand_file.close()


    #Target-Disease data
    skip = 0
    disease_res = []
    while True:
        res = client.execute(gql(disease_query_string.format(100000,skip)))
        if len(res['download']['data'])>0:
            disease_res.extend(res['download']['data'])
            skip +=100000
        else:
            break
    disease_file = open(project_dir / 'data/raw/pharos_all_target_diseases.csv', "w")
    disease_writer = csv.DictWriter(
       disease_file,fieldnames=disease_res[0].keys()
    )
    disease_writer.writeheader()
    disease_writer.writerows(disease_res)
    disease_file.close()

if __name__=="__main__":
    main()
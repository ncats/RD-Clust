from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import json
from pathlib import Path



def main():
    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url="https://pharos-api.ncats.io/graphql")

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True,execute_timeout=None)

    count_query = gql(
        """
        query {
            targets{
                count
            }
        }
        """
    )

    tchem_query_1='''
    query facetsForAllTargets {
        targets (filter: {
            facets: [{
                facet: "Target Development Level",
                values: ["Tchem"]
            }]
        }) {
            count
            targets (top:1930){
            name
            tdl
            fam
            sym
            ligands {
                ligid
                name
                isdrug
            }
            }
        }
    }
    '''

    tchem_query_1='''
    query facetsForAllTargets {
        targets (filter: {
            facets: [{
                facet: "Target Development Level",
                values: ["Tchem"]
            }]
        }) {
            count
            targets (top:1930){
            name
            tdl
            fam
            sym
            ligands {
                ligid
                name
                isdrug
            }
            }
        }
    }
    '''

    tchem_query_2='''
    query {
        targets (filter: {
            facets: [{
                facet: "Target Development Level",
                values: ["Tchem"]
            }]
        }) {
            count
            targets (top:1930){
            name
            tdl
            fam
            sym
            ligands {
                ligid
                name
                isdrug
            }
            }
        }
    }
    '''

    target_query_string = '''query {{
            targets( 
                filter: {{
                facets: [{{
                    facet: "Target Development Level",
                    values: ["Tchem"]
                }}]
                }}
            ) {{
                count
                targets(top: {0} ){{
                    sym
                    name
                    tdl
                    ligands {{
                        ligid
                        name
                        isdrug
                        synonyms {{
                            name
                            value
                        }}
                    }}
                    diseases {{
                        name
                        dids{{
                            id
                            dataSources
                        }}
                        associations{{
                            disassid
                            type
                            name
                            did
                            source
                        }}
                    }}
                }}
            }}
        }}
    '''    

    # Execute the query on the transport
    count_res = client.execute(count_query)

    total_targets= count_res['targets']['count']

    target_res_1 = client.execute(gql(tchem_query_1))
    target_res_2 = client.execute(gql(tchem_query_2))

    project_dir = Path(__file__).resolve().parents[2]
    f = open(project_dir / 'data/raw/pharos_tchem_ligands_1.json', "w")
    json.dump(target_res_1, f,indent=4)
    f.close()

    f = open(project_dir / 'data/raw/pharos_tchem_ligands_2.json', "w")
    json.dump(target_res_2, f,indent=4)
    f.close()

if __name__=="__main__":
    main()
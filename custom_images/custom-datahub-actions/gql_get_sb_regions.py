from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import os

ENV = os.getenv('ENV', 'stg')


def get_sb_regions(gms_endpoint: str, token: str, gql_query: str,
                   platform: str, sb_region_index_from_name: int):
  transport = AIOHTTPTransport(url=f'{gms_endpoint}/api/graphql',
                               headers={'Authorization': f'Bearer {token}'})

  # Create a GraphQL client using the defined transport
  client = Client(transport=transport, fetch_schema_from_transport=True)

  # Execute the query on the transport
  # Provide a GraphQL query
  query = gql(f'''
    {{
      search(
        input: {{ 
          type: DATASET,
          query: "{gql_query}",
          start: 0,
          count: 100,
          orFilters: [
            {{
              and: [
                {{
                  field: "platform",
                  values: [
                    "urn:li:dataPlatform:{platform}" 
                  ]
                }},
                {{
                  field: "origin",
                  values: [
                    "{ENV.upper()}"
                  ]
                }}
              ]
            }}
          ]
        }}
      )
      {{
        start
        count
        total
        searchResults {{
          entity {{
             urn
             ...on Dataset {{
                name
             }}
          }}
          matchedFields {{
            name
            value
          }}
        }}
      }}
    }}
    ''')
  result = client.execute(query)
  serachResults = result['search']['searchResults']

  sb_regions = []
  for entDict in serachResults:
    name = entDict['entity']['name']
    sb_region = name.split('.')[sb_region_index_from_name]
    sb_regions.append(sb_region)
    print(sb_region, name)
  return sb_regions

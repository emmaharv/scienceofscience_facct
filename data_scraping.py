import numpy as np
import pandas as pd
import requests
import re
from habanero import Crossref
from pybtex.database import parse_file
from bs4 import BeautifulSoup

## Call crossref API
cr = Crossref()

## Read data
bib_data = parse_file('data/acm.bib')

## Create authorship network at FAccT
edges = pd.DataFrame(columns=['v', 'w', 'year'])
nodes = pd.DataFrame(columns=['n', 'year'])
for key in bib_data.entries:

    year = bib_data.entries[key].fields['year']

    authors = [str(author) for author in bib_data.entries[key].persons['author']]
    authors_v = pd.DataFrame({'v' : authors})
    authors_w = pd.DataFrame({'w' : authors})

    nodes_temp = pd.DataFrame({'n' : authors})
    nodes_temp['year'] = year

    edges_temp = authors_v.merge(authors_w, how='cross')
    edges_temp['year'] = year
    edges_temp = edges_temp[edges_temp['v'] < edges_temp['w']]

    edges = pd.concat([edges, edges_temp], ignore_index=True)
    nodes = pd.concat([nodes, nodes_temp], ignore_index=True)

for year in nodes.year.unique():

    nodes_year = nodes[nodes['year'] <= year]
    edges_year = edges[edges['year'] <= year]

    nodes_year = nodes_year.drop(columns=['year'])
    edges_year = edges_year.drop(columns=['year'])

    nodes_year = nodes_year.drop_duplicates()
    edges_year['weight'] = 1
    edges_year = edges_year.groupby(['v', 'w']).sum().reset_index()

    nodes_year.to_csv('data/nodes_' + year + '.csv', index=False)
    edges_year.to_csv('data/edges_' + year + '.csv', index=False)


## Get all references of each paper
references = pd.DataFrame(columns=['id', 'reference_id'])
for key in bib_data.entries:
    metadata = cr.works(ids = key)

    try:
        metadata_references = metadata['message']['reference']

        references_list = []
        for reference in metadata_references:
            try:
                doi = reference['DOI']
                references_list.append(doi)

            except: 
                pass

        if len(references_list) > 0:
            references_temp = pd.DataFrame({'id' : key, 'reference_id' : references_list})
            references = pd.concat([references, references_temp], ignore_index=True)

    except:
        print(key)
        pass

references.to_csv('data/reference_map.csv', index=False)

## Get all citations of each paper
citations = pd.DataFrame(columns=['id', 'citation_url', 'citation_doi', 'citation_title'])
for key in bib_data.entries:

    r = requests.get('https://dl.acm.org/action/ajaxShowCitedBy?doi=' + key)

    if (r.url == 'https://dl.acm.org/doi/abs/' + key):
        continue

    html = BeautifulSoup(r.text, 'html.parser')

    url_list = []
    doi_list = []
    title_list = []
    for li in html.find_all('li', class_='references__item'):

        url = li.find('a', class_='link')
        if url is not None: 
            url = url.get('href')

        doi = li.find('span', class_='doi')
        if doi is not None: 
            doi = doi.text

        title = li.find('span', class_='references__article-title')
        if title is not None: 
            title = title.text

        url_list.append(url)
        doi_list.append(doi)
        title_list.append(title)

    citations_temp = pd.DataFrame({'id' : key, 'citation_url' : url_list, 
                                    'citation_doi' : doi_list, 'citation_title' : title_list})
    citations = pd.concat([citations, citations_temp], ignore_index=True)
    
citations.to_csv('data/citation_map.csv', index=False)
citations = pd.read_csv('data/citation_map.csv')

citations['doi_combined'] = np.where(~citations['citation_doi'].isnull(), citations['citation_doi'],
                                    np.where(citations['citation_url'].str.contains('/10.', regex=False), 
                                            citations['citation_url'].str.replace('.*\/10\.', '10.', n=1, regex=True), None))

citations = citations[~citations['doi_combined'].isnull()]
citations['citation_id'] = citations['doi_combined']
citations = citations.drop(columns=['citation_url', 'citation_title', 'doi_combined', 'citation_doi'])

citations.to_csv('data/citation_map.csv', index=False)
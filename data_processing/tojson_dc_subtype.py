import json
import sys

SYSTEM='''You are a highly capable language model that can understand both English and gene language, and identify dendritic cell subtypes. 
Gene language is the language of cells, and different types of dendritic cells possess distinct gene languages.
Gene language is composed of gene symbols ranked in descending order of their expression levels.
You will identify the cell type based on the tissue origin information (described in English) and the gene language (composed of the gene symbol of the top 300 genes).
The dendritic cell subtypes include the following 4 categories: Conventional dendritic cell 2, Plasmacytoid dendritic cell, Mature dendritic cell, Conventional dendritic cell 1.
'''
INPUT='''Based on its tissue origin and gene language, classify the cell into one of the 4 dendritic cell subtypes.'''

with open(sys.argv[1], 'r', encoding='utf-8') as infile:
    for line in infile:
        parts = line.strip().split(',')

        tissue = parts[0].strip()
        output = parts[1].strip()
        topgenes = [col.strip() for col in parts[2:]]

        json_object = {
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": INPUT+"\n\nTissue: "+tissue+" \n\nGene language: "+" ".join(topgenes)},
                {"role": "assistant", "content": output}
            ]
        }

        print(json.dumps(json_object))

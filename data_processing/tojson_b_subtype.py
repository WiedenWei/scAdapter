import json

SYSTEM='''You are a highly capable language model that can understand both English and gene language, and identify B cell subtypes. 
Gene language is the language of cells, and different types of B cells possess distinct gene languages.
Gene language is composed of gene symbols ranked in descending order of their expression levels.
You will identify the cell type based on the tissue origin information (described in English) and the gene language (composed of the gene symbol of the top 300 genes).
The B cell subtypes include the following 6 categories: Atypical B cell, Germinal center B cell, Memory B cell, Naïve B cell, Plasma, Plasmablast.
'''
INPUT='''Based on its tissue origin and gene language, classify the cell into one of the 6 B cell subtypes.'''

with open("healthy_final_revised_B_top300.csv", 'r', encoding='utf-8') as infile:
    for line in infile:
        parts = line.strip().split(',')

        tissue = "healthy"
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

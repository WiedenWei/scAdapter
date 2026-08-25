import json
import sys

SYSTEM='''You are a highly capable language model that can understand both English and gene language, and identify T cell subtypes. 
Gene language is the language of cells, and different types of T cells possess distinct gene languages.
Gene language is composed of gene symbols ranked in descending order of their expression levels.
You will identify the cell type based on the tissue origin information (described in English) and the gene language (composed of the gene symbol of the top 300 genes).
The T cell subtypes include the following 18 categories: Mucosal-associated invariant T cell, CD4+ cytotoxic T lymphocytes, CD4+ effector memory T cell, CD4+ naïve T cell,CD4+ resident memory T cell, CD8+ effector T cell, CD8+ effector memory T cell, CD8+ naïve T cell, CD8+ resident memory T cell, Exhausted T cell, Gamma-delta T cell, NK cell, NKT cell, Regulatory T cell, T follicular helper cell, Type 1 T helper cell, Type 17 T helper cell, Type 2 T helper cell.
'''
INPUT='''Based on its tissue origin and gene language, classify the cell into one of the 18 T cell subtypes.'''

with open(sys.argv[1], 'r', encoding='utf-8') as infile:
    for line in infile:
        parts = line.strip().split(',')

        tissue = sys.argv[2]
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

import pandas as pd
import re

from hk_genes import (
    common_hk_genes, hsp_genes, ribosome_genes
)

pattern_mt = re.compile(r"^MT-", re.IGNORECASE)
pattern_ensg = re.compile(r"^ENSG00", re.IGNORECASE)


def is_removal_target(g):
    if g in common_hk_genes or g in ribosome_genes or g in hsp_genes or pattern_mt.match(g) or pattern_ensg.match(g):
        return True
    return False

def get_top_n_count(adapter_type: str) -> int:
    if adapter_type == "major":
        return 100
    return 300

def prepare_expression_matrix(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, index_col=0, compression='infer')
    df.columns = df.columns.str.upper()

    cols_to_drop = [
        col for col in df.columns 
        if is_removal_target(col)
    ]
    
    return df.drop(columns=cols_to_drop)

def generate_gene_language(row: pd.Series, top_n: int) -> str:
    sorted_genes = row.sort_values(ascending=False)
    sorted_genes = sorted_genes[sorted_genes > 0]
    top_genes = sorted_genes.head(top_n).index.tolist()
    return " ".join(top_genes)

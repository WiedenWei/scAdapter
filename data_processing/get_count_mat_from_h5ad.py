import argparse
import scanpy as sc
import pandas as pd
import scipy.sparse as sp

def get_gene_names_from_feature_name(adata, raw_adata, gene_name_col="feature_name"):

    if gene_name_col in adata.var.columns:
        print(f"Using adata.var['{gene_name_col}'] as gene names")
        gene_names = adata.var[gene_name_col].astype(str).values

        if len(gene_names) != raw_adata.shape[1]:
            raise ValueError(
                f"adata.var['{gene_name_col}'] length is {len(gene_names)}, "
                f"but raw count matrix has {raw_adata.shape[1]} genes. "
                "The gene annotation does not match adata.raw.X."
            )
    
    elif gene_name_col in raw_adata.var.columns:
        print(f"Using raw.var['{gene_name_col}'] as gene names")
        gene_names = raw_adata.var[gene_name_col].astype(str).values

    else:
        print(f"'{gene_name_col}' not found. Using raw.var_names instead.")
        gene_names = raw_adata.var_names.astype(str).values

    return gene_names


def main():
    parser = argparse.ArgumentParser(
        description="Export raw count matrix from an h5ad file."
    )

    parser.add_argument(
        "--h5ad_file",
        required=True,
        type=str,
        help="Path to the input .h5ad file"
    )

    parser.add_argument(
        "--cell_id_file",
        required=True,
        type=str,
        help="Text file containing target cell IDs, one cell ID per line"
    )

    parser.add_argument(
        "--output_csv",
        type=str,
        default="raw_count_matrix.csv",
        help="Output CSV file"
    )

    parser.add_argument(
        "--gene_name_col",
        type=str,
        default="feature_name",
        help="Column storing gene names, usually feature_name"
    )

    args = parser.parse_args()

    print(f"Loading h5ad file: {args.h5ad_file}")
    adata = sc.read_h5ad(args.h5ad_file)

    print(f"Original AnnData shape: {adata.shape}")

    if adata.raw is None:
        raise ValueError(
            "adata.raw is None. The raw count matrix is not available in this h5ad file."
        )

    print(f"Loading target cell IDs from: {args.cell_id_file}")
    with open(args.cell_id_file, "r") as f:
        target_cells = [line.strip() for line in f if line.strip()]

    target_cells = list(dict.fromkeys(target_cells))

    existing_cells = [cell for cell in target_cells if cell in adata.obs_names]
    missing_cells = [cell for cell in target_cells if cell not in adata.obs_names]

    print(f"Requested cells: {len(target_cells)}")
    print(f"Found cells: {len(existing_cells)}")
    print(f"Missing cells: {len(missing_cells)}")

    if len(existing_cells) == 0:
        raise ValueError("None of the target cell IDs were found in adata.obs_names.")

    print("Subsetting AnnData by selected cells...")
    adata = adata[existing_cells, :].copy()
    print(f"Subset AnnData shape: {adata.shape}")

    print("Extracting raw count matrix from adata.raw.X...")
    raw_adata = adata.raw.to_adata()

    print(f"Raw count matrix shape: {raw_adata.shape}")

    gene_names = get_gene_names_from_feature_name(
        adata=adata,
        raw_adata=raw_adata,
        gene_name_col=args.gene_name_col
    )

    gene_names = pd.Index(gene_names).astype(str)
    gene_names = gene_names.to_series().groupby(gene_names).cumcount().astype(str).radd("_").where(
        gene_names.duplicated(), ""
    ).radd(gene_names)

    matrix = raw_adata.X

    if sp.issparse(matrix):
        print("Converting sparse matrix to dense matrix...")
        matrix = matrix.toarray()

    print("Creating DataFrame...")
    df = pd.DataFrame(
        data=matrix.T,
        index=gene_names,
        columns=adata.obs_names
    )

    print(f"Writing raw count matrix to: {args.output_csv}")
    df.to_csv(args.output_csv)

    print("Done.")


if __name__ == "__main__":
    main()

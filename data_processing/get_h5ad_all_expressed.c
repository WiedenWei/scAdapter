#include "hdf5.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct {
    int gene_idx;
    float expression;
} GeneExpr;

int compare_genes(const void* a, const void* b) {
    GeneExpr* geneA = (GeneExpr*)a;
    GeneExpr* geneB = (GeneExpr*)b;
    
    if (geneA->expression < geneB->expression) return 1;
    if (geneA->expression > geneB->expression) return -1;
    
    if (geneA->gene_idx < geneB->gene_idx) return -1;
    if (geneA->gene_idx > geneB->gene_idx) return 1;
    
    return 0;
}

void check_hdf5_error(herr_t status, const char* message) {
    if (status < 0) {
        fprintf(stderr, "HDF5 Error: %s\n", message);
        exit(EXIT_FAILURE);
    }
}

void read_string_dataset(hid_t file_id, const char* dset_name, hsize_t* num_items, char*** string_array) {
    hid_t dset_id = H5Dopen2(file_id, dset_name, H5P_DEFAULT);
    check_hdf5_error(dset_id, "Failed to open dataset");

    hid_t space_id = H5Dget_space(dset_id);
    *num_items = H5Sget_simple_extent_npoints(space_id);

    hid_t mem_type_id = H5Tcopy(H5T_C_S1);
    H5Tset_size(mem_type_id, H5T_VARIABLE);
    H5Tset_cset(mem_type_id, H5T_CSET_UTF8);

    *string_array = (char**)malloc(*num_items * sizeof(char*));
    check_hdf5_error(H5Dread(dset_id, mem_type_id, H5S_ALL, H5S_ALL, H5P_DEFAULT, *string_array), "Failed to read string dataset");

    H5Tclose(mem_type_id);
    H5Sclose(space_id);
    H5Dclose(dset_id);
}

void* read_numeric_dataset(hid_t file_id, const char* dset_name, hid_t mem_type_id, hsize_t* out_num_items) {
    hid_t dset_id = H5Dopen2(file_id, dset_name, H5P_DEFAULT);
    check_hdf5_error(dset_id, "Failed to open numeric dataset");

    hid_t space_id = H5Dget_space(dset_id);
    hsize_t num_items = H5Sget_simple_extent_npoints(space_id);
    if (out_num_items != NULL) {
        *out_num_items = num_items;
    }

    void* buffer = malloc(num_items * H5Tget_size(mem_type_id));
    if (!buffer) {
        fprintf(stderr, "Failed to allocate memory for numeric dataset\n");
        exit(EXIT_FAILURE);
    }

    check_hdf5_error(H5Dread(dset_id, mem_type_id, H5S_ALL, H5S_ALL, H5P_DEFAULT, buffer), "Failed to read numeric dataset");

    H5Sclose(space_id);
    H5Dclose(dset_id);
    return buffer;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <input.h5ad> <output.csv>\n", argv[0]);
        return 1;
    }

    const char* h5ad_file = argv[1];
    const char* csv_file = argv[2];

    printf("▶️ Starting processing of %s\n", h5ad_file);

    hid_t file_id = H5Fopen(h5ad_file, H5F_ACC_RDONLY, H5P_DEFAULT);
    check_hdf5_error(file_id, "Could not open H5AD file.");

    hsize_t num_unique_symbols;
    char** gene_symbol_categories;
    printf("Reading gene symbols...\n");
    read_string_dataset(file_id, "/var/feature_name/categories", &num_unique_symbols, &gene_symbol_categories);
    
    hsize_t num_genes; 
    int* gene_symbol_codes = (int*)read_numeric_dataset(file_id, "/var/feature_name/codes", H5T_NATIVE_INT, &num_genes);

    hsize_t num_unique_cell_ids;
    char** cell_id_categories;
    printf("Reading cell IDs (categories and codes)...\n");
    read_string_dataset(file_id, "/obs/cell_id/categories", &num_unique_cell_ids, &cell_id_categories);

    hsize_t num_cells; // The length of the codes array tells us the total number of cells
    int* cell_id_codes = (int*)read_numeric_dataset(file_id, "/obs/cell_id/codes", H5T_NATIVE_INT, &num_cells);
    printf("✅ Found %lu cells (%lu unique IDs).\n", num_cells, num_unique_cell_ids);

    hsize_t num_categories_celltype1;
    char** cell_type1_categories;
    read_string_dataset(file_id, "/obs/cell_type/categories", &num_categories_celltype1, &cell_type1_categories);
    int* cell_type1_codes = (int*)read_numeric_dataset(file_id, "/obs/cell_type/codes", H5T_NATIVE_INT, NULL);

    printf("Reading expression data (CSR matrix)...\n");
    int64_t* indptr = (int64_t*)read_numeric_dataset(file_id, "/X/indptr", H5T_NATIVE_INT64, NULL); 
    int* indices = (int*)read_numeric_dataset(file_id, "/X/indices", H5T_NATIVE_INT, NULL);
    float* data = (float*)read_numeric_dataset(file_id, "/X/data", H5T_NATIVE_FLOAT, NULL);

    FILE* fp_out = fopen(csv_file, "w");
    if (!fp_out) {
        fprintf(stderr, "Error: Could not open output file %s\n", csv_file);
        return 1;
    }

    printf("⚙️ Processing cells and writing to %s...\n", csv_file);
    for (hsize_t i = 0; i < num_cells; ++i) {
        
        int current_cell_code = cell_id_codes[i];
        const char* current_cell_id = "UnknownCellID";
        if (current_cell_code >= 0 && current_cell_code < num_unique_cell_ids) {
            current_cell_id = cell_id_categories[current_cell_code];
        }

        int celltype1_code = cell_type1_codes[i];
        const char* cell_identity_type1 = (celltype1_code >= 0 && celltype1_code < num_categories_celltype1) ? cell_type1_categories[celltype1_code] : "Unknown";

        int64_t start = indptr[i];
        int64_t end = indptr[i+1];
        int64_t num_expressed_genes = end - start;

        if (num_expressed_genes <= 0) {
            fprintf(fp_out, "%s,OV,%s\n", current_cell_id, cell_identity_type1);
            continue;
        }

        GeneExpr* expressed_genes = (GeneExpr*)malloc(num_expressed_genes * sizeof(GeneExpr));
        if (!expressed_genes) continue; 

        for (int64_t j = 0; j < num_expressed_genes; ++j) {
            expressed_genes[j].gene_idx = indices[start + j];
            expressed_genes[j].expression = data[start + j];
        }

        qsort(expressed_genes, num_expressed_genes, sizeof(GeneExpr), compare_genes);

        fprintf(fp_out, "%s,OV,%s", current_cell_id, cell_identity_type1);

        for (int64_t k = 0; k < num_expressed_genes; ++k) {
            int top_gene_idx = expressed_genes[k].gene_idx;
            
            if (top_gene_idx >= 0 && top_gene_idx < num_genes) {
                int symbol_code = gene_symbol_codes[top_gene_idx];
                
                if (symbol_code >= 0 && symbol_code < num_unique_symbols) {
                    fprintf(fp_out, ",%s", gene_symbol_categories[symbol_code]);
                }
            }
        }
        fprintf(fp_out, "\n");

        free(expressed_genes);
    }

    printf("✅ Success! Output written to %s.\n", csv_file);

    fclose(fp_out);
    free(indptr);
    free(indices);
    free(data);
    
    free(gene_symbol_categories);
    free(gene_symbol_codes); 
    
    free(cell_id_categories);
    free(cell_id_codes);
    
    free(cell_type1_categories);
    free(cell_type1_codes);
    
    H5Fclose(file_id);

    return 0;

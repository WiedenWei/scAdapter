import sys
import re

if len(sys.argv) != 4:
    print("Usage: python remove_housekeeping_genes.py ribosome_genes.txt hsp_genes.txt input.txt")
    sys.exit(1)

ribosome_genes = []
with open(sys.argv[1]) as f:
    for line in f:
        ribosome_genes.append(line.strip())

hsp_genes = []
with open(sys.argv[2]) as f:
    for line in f:
        hsp_genes.append(line.strip())

pattern_mt = re.compile(r"^MT-", re.IGNORECASE)

pattern_ensg = re.compile(r"^ENSG00", re.IGNORECASE)

common_hk_genes = [
    "GAPDH", "ACTB", "B2M", "PPIA", "HPRT1", "TBP", "UBC", "YWHAZ",
    "PGK1", "SDHA", "HMBS", "GUSB", "ATP5B", "ALAS1", "TFRC", 
    "G6PD", "FTH1", "MALAT1", "TMSB4X", "FTL", "EIF5", "EIF5B",
    "EEF1A1", "EEF1A2", "EEF1B2", "EEF1D", "EEF1G", "EEF1E1", "EEF2",
    "EIF1", "EIF1B", "EIF1AX", "EIF1AY", "EIF2S1", "EIF2S2", "EIF2S3", 
    "EIF2B1", "EIF2B2", "EIF2B3", "EIF2B4", "EIF2B5", "EIF4A1", "EIF4A2",
    "EIF4A3", "EIF4E", "EIF4E2", "EIF4E3", "EIF4G1", "EIF4G2", "EIF4G3"
]

def is_removal_target(g):
    if g in common_hk_genes or g in ribosome_genes or g in hsp_genes or pattern_mt.match(g) or pattern_ensg.match(g):
        return True

    return False

with open(sys.argv[3], 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split(',')
        cell_id = parts[0].strip()
        cancer_type = parts[1].strip()
        cell_type = parts[2].strip()
        genes = [col.strip() for col in parts[3:]]
        clear_genes = [gene for gene in genes if not is_removal_target(gene)]
        print(",".join([cell_id, cancer_type, cell_type] + clear_genes))

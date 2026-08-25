import asyncio
import traceback
import os
import httpx
import pandas as pd

from parser import prepare_expression_matrix, get_top_n_count, generate_gene_language
from inference import annotate_single_cell
from notifier import send_result_email

from prompts import (
    cancer_major_user, healthy_major_user, t_subtype_user, b_subtype_user, dc_subtype_user, mm_subtype_user,
    cancer_major_system, healthy_major_system, t_subtype_system, b_subtype_system, dc_subtype_system, mm_subtype_system 
)

def get_system_user(annotation_type: str, tissue_type: str, tissue_status: str):
    if annotation_type == "major" and tissue_status == "healthy":
        system = healthy_major_system
        user = healthy_major_user
        tissue = tissue_type
        adapter = "healthy_major"
    elif annotation_type == "major" and tissue_status == "cancerous":
        system = cancer_major_system
        user = cancer_major_user
        tissue = tissue_type
        adapter = "cancer_major"
    elif annotation_type == "t_subtype":
        system = t_subtype_user
        user = t_subtype_system
        tissue = tissue_status
        if tissue_status == "cancerous":
            adapter = "cancer_t"
        else:
            adapter = "healthy_t"
    elif annotation_type == "b_subtype":
        system = b_subtype_user
        user = b_subtype_system
        tissue = tissue_status
        if tissue_status == "cancerous":
            adapter = "cancer_b"
        else:
            adapter = "healthy_b"
    elif annotation_type == "dc_subtype":
        system = dc_subtype_user
        user = dc_subtype_system
        tissue = tissue_status
        if tissue_status == "cancerous":
            adapter = "cancer_dc"
        else:
            adapter = "healthy_dc"
    elif annotation_type == "mm_subtype":
        system = mm_subtype_user
        user = mm_subtype_system
        tissue = tissue_status
        if tissue_status == "cancerous":
            adapter = "cancer_mm"
        else:
            adapter = "healthy_mm"
    else :
        system = ""
        user = ""
        tissue = ""
        adapter = ""
    return system, user, tissue, adapter

async def process_job_queue(job_queue: asyncio.Queue, job_states: dict):
    print("Background worker initialized and waiting for jobs...")
    
    while True:

        job_data = await job_queue.get()
        job_id = job_data["job_id"]
        
        job_states[job_id]["status"] = "Processing"
        print(f"\n[START] Job {job_id} for {job_data['email']}")

        try:
            df = prepare_expression_matrix(job_data["file_path"])
            top_n = get_top_n_count(job_data["annotation_type"])
            
            annotated_labels = []
            total_cells = len(df)

            async with httpx.AsyncClient(verify=False) as client:
                for index, (row_label, row_data) in enumerate(df.iterrows()):
                    
                    gene_language = generate_gene_language(row_data, top_n)
                    
                    system, user, tissue, adapter = get_system_user(job_data["annotation_type"],
                                                           job_data["tissue_type"],
                                                           job_data["tissue_state"])
                    
                    message_payload = [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user+"\n\nTissue: "+tissue+"\n\nGene language: "+gene_language}
                    ]
                    
                    # 4. Fire the inference request
                    prediction = await annotate_single_cell(
                        client=client,
                        adapter_type=adapter,
                        message=message_payload
                    )
                    
                    prediction = prediction.replace("analysisassistantfinal", "").replace("analysisassistantcommentaryassistantfinal", "")
                    annotated_labels.append(prediction)
                    
                    if (index + 1) % 100 == 0 or (index + 1) == total_cells:
                        print(f"  -> {index + 1}/{total_cells} cells annotated...")

            results_df = pd.DataFrame(
                {"scAdapter_Annotation": annotated_labels}, 
                index=df.index
            )
            
            results_df.index.name = "cell_id"
            
            result_path = f"./data/results/{job_id}_annotated.csv"
            results_df.to_csv(result_path)
            
            await send_result_email(job_data["email"], job_id, result_path)
            
            job_states[job_id]["status"] = "Completed"
            print(f"[SUCCESS] Job {job_id} finished.")

        except Exception as e:
            print(f"[FAILED] Job {job_id} Error:\n{traceback.format_exc()}")
            job_states[job_id]["status"] = "Failed"
            
        finally:
            if os.path.exists(job_data["file_path"]):
                os.remove(job_data["file_path"])
                
            job_queue.task_done()

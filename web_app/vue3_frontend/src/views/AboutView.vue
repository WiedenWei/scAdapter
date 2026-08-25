<template>
  <div class="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-sm border border-gray-100">
    <h1 class="text-3xl font-bold mb-6 text-gray-900">How scAdapter Works</h1>
    
    <div class="w-full mb-8 rounded-lg overflow-hidden border border-gray-200 shadow-sm bg-gray-50">
      <img src="../assets/1.png" alt="scAdapter Workflow" class="w-full h-auto block" />
    </div>

    <div class="space-y-6 text-gray-700 leading-relaxed">
      <section>
        <h2 class="text-xl font-bold text-gray-900 mb-2">1. Gene Language Translation</h2>
        <p>Unlike traditional methods that rely on clustering, scAdapter processes single-cell data at the individual cell level. It transforms your raw cell-by-gene expression matrix into a ranked "gene language," ordering genes by their expression magnitude. This discrete representation captures the unique transcriptomic hierarchy of each cell.</p>
      </section>

      <section>
        <h2 class="text-xl font-bold text-gray-900 mb-2">2. Transformer-Based Inference</h2>
        <p>The ranked gene lists are fed into a fine-tuned Large Language Model (GPT-OSS-20B) equipped with specific Low-Rank Adaptation (LoRA) modules. Through its self-attention mechanism, the model naturally prioritizes canonical marker genes while discounting non-informative transcripts, avoiding the batch-effect vulnerabilities of dimensional reduction.</p>
      </section>

      <section>
        <h2 class="text-xl font-bold text-gray-900 mb-2">3. Hierarchical Annotation</h2>
        <p>The backend evaluates the cells using a two-step hierarchical logic. It first assigns a broad major cell lineage (e.g., T cell, B cell, Fibroblast) and subsequently deploys specialized subtype adapters to map high-resolution immune states (e.g., exhausted CD8+ T cells, regulatory T cells), returning standardized nomenclatures directly to you.</p>
      </section>
    </div>
  </div>
</template>
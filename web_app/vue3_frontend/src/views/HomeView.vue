<template>
  <div class="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-sm border border-gray-100">
    <h1 class="text-2xl font-bold mb-2">Automated Cell Type Annotation</h1>
    <p class="text-gray-600 mb-6">Upload your single-cell expression matrix (.csv) to generate high-resolution annotations via scAdapter.</p>
    
    <form @submit.prevent="submitJob" class="space-y-6">
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Annotation Target</label>
        <select 
          v-model="annotationType"
          class="w-full px-4 py-2 border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          required
        >
          <option value="major">Major Cell Types</option>
          <option value="t_subtype">T Cell Subtypes</option>
          <option value="b_subtype">B Cell Subtypes</option>
          <option value="dc_subtype">Dendritic Cell (DC) Subtypes</option>
          <option value="mm_subtype">Monocyte / Macrophage Subtypes</option>
        </select>
        <p class="text-xs text-gray-500 mt-1">Select the specific LoRA adapter network for your dataset.</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Tissue State</label>
        <div class="flex space-x-6">
          <label class="inline-flex items-center cursor-pointer">
            <input 
              type="radio" 
              v-model="tissueCondition" 
              value="healthy" 
              class="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            >
            <span class="ml-2 text-gray-700 font-medium">Healthy Tissue</span>
          </label>
          <label class="inline-flex items-center cursor-pointer">
            <input 
              type="radio" 
              v-model="tissueCondition" 
              value="cancer" 
              class="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            >
            <span class="ml-2 text-gray-700 font-medium">Cancer / Tumor</span>
          </label>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Specific Tissue Origin</label>
        <select 
          v-model="tissueType"
          class="w-full px-4 py-2 border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          required
        >
          <option value="" disabled>Select a tissue type...</option>
          <option v-for="tissue in availableTissues" :key="tissue" :value="tissue">
            {{ tissue }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Cell-by-Gene Matrix (.csv.gz, csv.xz, .csv.zip, .csv.bz2, .csv)</label>
        <input 
          type="file" 
          accept=".csv,.gz,.xz,.zip,.bz2"
          @change="handleFileChange"
          class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          required
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Notification Email</label>
        <input 
          v-model="email" 
          type="email" 
          placeholder="researcher@university.edu"
          class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          required
        />
        <p class="text-xs text-gray-500 mt-1">We will send a download link when your job completes.</p>
      </div>

      <button 
        type="submit" 
        :disabled="isSubmitting"
        class="w-full bg-blue-600 text-white font-medium py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
      >
        {{ isSubmitting ? 'Uploading...' : 'Submit Job' }}
      </button>
    </form>

    <div v-if="jobId" class="mt-6 p-4 bg-green-50 text-green-800 rounded-md border border-green-200">
      Job successfully submitted! Your Job ID is: <span class="font-mono font-bold">{{ jobId }}</span>. 
      <br>
      <router-link :to="`/status?id=${jobId}`" class="underline font-medium hover:text-green-900">
        Track your job status here.
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

// --- Form State ---
const annotationType = ref<string>('major')
const tissueCondition = ref<'healthy' | 'cancerous'>('healthy')
const tissueType = ref<string>('Bladder') // Default starting value
const file = ref<File | null>(null)
const email = ref<string>('')

// --- Submission State ---
const isSubmitting = ref<boolean>(false)
const jobId = ref<string | null>(null)

// --- Data Dictionaries (Alphabetized for better UX) ---
const healthyTissues = [
  "Bladder", "Blood", "BoneMarrow", "Breast", "Colon", "CommonBileDuct", 
  "Esophagus", "Eye", "Fat", "Heart", "Kidney", "Liver", "Lung", "LymphNode", 
  "Nose", "Omentum", "Oral", "Ovary", "Pancreas", "Prostate", "Rectum", 
  "SalivaryGland", "SkeletalMuscle", "Skin", "SmallIntestine", "Spleen", 
  "Stomach", "Testis", "Thymus", "Tongue", "Trachea", "Ureter", "Uterus", 
  "Vagina", "Vasculature"
]

const cancerTissues = [
  "ALM", "ATC", "BLCA", "BRCA", "CACC", "CESC", "CHC", "Chondroblastic OS", 
  "Conventional OS", "CRC", "CSCC", "cSCC", "DCIS", "ESCC", "GCTB", "HCC", 
  "HGSOC", "HNSC", "ICC", "IDC", "Intraosseous OS", "KICH", "KIRC", "KIRP", 
  "KNPC", "LUAD", "LUAD(SSN)", "LYM", "NB", "NET", "NKNPC", "NPC", "OSCC", 
  "OV", "PAAD", "PDAC", "PRAD", "PTC", "SKCM", "STAD", "TGCT", "TNBC", "UVM"
]

// --- Computed Logic ---
const availableTissues = computed(() => {
  return tissueCondition.value === 'healthy' ? healthyTissues : cancerTissues
})

// Automatically reset the dropdown to the first item when the user switches between Healthy/Cancer
watch(tissueCondition, () => {
  tissueType.value = availableTissues.value[0]!
})

// --- Event Handlers ---
const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    file.value = target.files.item(0)
  }
}

const submitJob = async () => {
  if (!file.value || !email.value || !annotationType.value || !tissueType.value) return
  
  isSubmitting.value = true
  const formData = new FormData()
  
  // Append all parameters for the FastAPI backend
  formData.append('annotation_type', annotationType.value)
  formData.append('tissue_state', tissueCondition.value)
  formData.append('tissue_type', tissueType.value)
  formData.append('file', file.value)
  formData.append('email', email.value)

  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    })
    
    if (response.ok) {
      const data = await response.json()
      jobId.value = data.job_id
      
      // Reset form fields
      file.value = null
      email.value = ''
      annotationType.value = 'major'
      tissueCondition.value = 'healthy'
      tissueType.value = 'Bladder'
      
      // Reset file input in DOM
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
      if (fileInput) fileInput.value = ''
      
    } else {
      alert("Upload failed. Please try again.")
    }
  } catch (error) {
    console.error("Error submitting job:", error)
    alert("An error occurred during submission.")
  } finally {
    isSubmitting.value = false
  }
}
</script>

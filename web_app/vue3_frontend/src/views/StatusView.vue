<template>
  <div class="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-sm border border-gray-100">
    <h1 class="text-2xl font-bold mb-6">Check Job Status</h1>
    
    <div class="flex space-x-4 mb-8">
      <input 
        v-model="queryId" 
        type="text" 
        placeholder="Enter your Job ID"
        class="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 font-mono"
      />
      <button 
        @click="checkStatus" 
        class="bg-gray-800 text-white font-medium py-2 px-6 rounded-md hover:bg-gray-900"
      >
        Search
      </button>
    </div>

    <!-- Status Display -->
    <div v-if="statusData" class="p-6 rounded-md border" :class="statusColorClass">
      <div class="flex items-center justify-between mb-4">
        <span class="font-bold text-lg">Status: {{ statusData.status }}</span>
        <span class="text-sm font-mono text-gray-500">ID: {{ statusData.job_id }}</span>
      </div>
      
      <p v-if="statusData.status === 'Queued'" class="text-gray-700">
        Your dataset is in the queue. There are <strong>{{ statusData.position }}</strong> jobs ahead of you.
      </p>
      
      <p v-if="statusData.status === 'Processing'" class="text-gray-700">
        scAdapter is currently processing your data on our GPUs. This usually takes a few minutes.
      </p>
      
      <div v-if="statusData.status === 'Completed'" class="text-green-700">
        <p class="mb-4">Annotation complete! An email has been sent to your inbox.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

interface JobStatus {
  job_id: string
  status: 'Queued' | 'Processing' | 'Completed' | 'Failed'
  position?: number
}

const route = useRoute()
const queryId = ref<string>('')
const statusData = ref<JobStatus | null>(null)

// Auto-fill and search if ID is in the URL (e.g., /status?id=123)
onMounted(() => {
  if (route.query.id) {
    queryId.value = route.query.id as string
    checkStatus()
  }
})

const statusColorClass = computed(() => {
  switch (statusData.value?.status) {
    case 'Queued': return 'bg-yellow-50 border-yellow-200'
    case 'Processing': return 'bg-blue-50 border-blue-200'
    case 'Completed': return 'bg-green-50 border-green-200'
    case 'Failed': return 'bg-red-50 border-red-200'
    default: return 'bg-gray-50 border-gray-200'
  }
})

const checkStatus = async () => {
  if (!queryId.value) return
  
  try {
    // Replace with your actual FastAPI endpoint
    const response = await fetch(`/api/status/${queryId.value}`)
    if (response.ok) {
      statusData.value = await response.json()
    } else {
      alert("Job ID not found.")
    }
  } catch (error) {
    console.error("Error fetching status:", error)
  }
}
</script>
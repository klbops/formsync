<template>
  <div class="min-h-screen bg-green-300 flex flex-col items-center justify-center p-4">
    <div class="bg-white p-8 rounded-xl shadow-lg max-w-md w-full">
      
      <h1 class="text-2xl font-bold text-green-600 text-center mb-2">FormSync</h1>
      <p class="text-gray-500 text-center mb-6">Sincronize sua planilha com o modelo Word.</p>

      <div class="space-y-4">
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Template (.docx)</label>
          <input type="file" @change="handleTemplate" accept=".docx" 
            class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Planilha (.xlsx, .xls)</label>
          <input type="file" @change="handleSpreadsheet" accept=".xlsx, .xls"
            class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100" />
        </div>

        <div v-if="previewRows.length > 0" class="mt-4 border border-gray-200 p-3 rounded-lg bg-gray-50">
          <div class="flex justify-between items-center mb-2">
            <label class="block text-sm font-bold text-gray-700">Selecione quem deseja gerar:</label>
            <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-semibold">
              📋 {{ selectedRows.length }}/{{ previewRows.length }}
            </span>
          </div>
          
          <div class="flex space-x-4 mb-3 border-b pb-2">
            <button @click="selectAll" class="text-xs font-semibold text-blue-600 hover:text-blue-800">✓ Marcar Todos</button>
            <button @click="deselectAll" class="text-xs font-semibold text-red-600 hover:text-red-800">✕ Desmarcar Todos</button>
          </div>

          <div class="max-h-40 overflow-y-auto space-y-1 pr-2">
            <label v-for="row in previewRows" :key="row.index" class="flex items-center space-x-2 cursor-pointer hover:bg-gray-100 p-1 rounded">
              <input type="checkbox" :value="row.index" v-model="selectedRows" class="form-checkbox text-blue-600 rounded">
              <span class="text-sm text-gray-700 truncate" :title="row.nome">{{ row.nome }}</span>
            </label>
          </div>
          <p class="text-xs text-gray-500 mt-2 text-right">{{ selectedRows.length }} selecionados</p>
        </div>

        <div class="pt-2">
          <label class="block text-sm font-medium text-gray-700 mb-2">Formato de Saída</label>
          <div class="flex space-x-6">
            <label class="inline-flex items-center cursor-pointer">
              <input type="radio" v-model="outputFormat" value="docx" class="form-radio text-blue-600 h-4 w-4">
              <span class="ml-2 text-gray-700">Word (.docx)</span>
            </label>
            <label class="inline-flex items-center cursor-pointer">
              <input type="radio" v-model="outputFormat" value="pdf" class="form-radio text-red-600 h-4 w-4">
              <span class="ml-2 text-gray-700">PDF (.pdf)</span>
            </label>
          </div>
        </div>

        <div v-if="loading" class="mt-4 space-y-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div class="flex items-center justify-center space-x-2">
            <div class="spinner"></div>
            <span class="text-sm font-semibold text-gray-700">A processar...</span>
          </div>

          <div class="text-center">
            <p class="text-xs text-gray-600 mb-1">
              <span v-if="processing.total > 0" class="font-bold text-blue-700">
                📁 {{ processing.current }}/{{ processing.total }} registos
              </span>
            </p>
            <p v-if="processing.status" class="text-xs text-gray-600 italic">
              {{ processing.status }}
            </p>
          </div>

          <div v-if="processing.total > 0" class="space-y-2">
            <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div 
                class="bg-gradient-to-r from-blue-500 to-blue-600 h-full transition-all duration-300 ease-out"
                :style="{ width: (processing.current / processing.total * 100) + '%' }"
              ></div>
            </div>
            <p class="text-xs text-gray-600 text-center font-semibold">
              {{ Math.round((processing.current / processing.total) * 100) }}%
            </p>
          </div>
        </div>

        <button 
          @click="generateDocs" 
          :disabled="loading || !fileTemplate || !fileSheet || (previewRows.length > 0 && selectedRows.length === 0)"
          class="w-full bg-green-600 text-white py-3 rounded-lg font-bold hover:bg-green-700 transition disabled:bg-gray-400 mt-4">
          {{ loading ? '⏳ A processar...' : '🚀 Gerar Documentos (.zip)' }}
        </button>
      </div>
      
      <p v-if="message" :class="`mt-4 text-center text-sm ${isError ? 'text-red-500' : 'text-green-500'}`">
        {{ message }}
      </p>
    </div>
  </div>
</template>

<style scoped>
/* Spinner animado */
.spinner {
  border: 3px solid rgba(59, 130, 246, 0.1);
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const fileTemplate = ref(null);
const fileSheet = ref(null);
const outputFormat = ref('docx');
const loading = ref(false);
const message = ref('');
const isError = ref(false);

// Controlo de pré-visualização e seleção
const previewRows = ref([]);
const selectedRows = ref([]);

// Rastreamento de processamento com status
const processing = ref({ 
  current: 0, 
  total: 0,
  status: '' 
});

const handleTemplate = (e) => { fileTemplate.value = e.target.files[0]; };

const handleSpreadsheet = async (e) => { 
  fileSheet.value = e.target.files[0]; 
  previewRows.value = [];
  selectedRows.value = [];
  message.value = '';
  
  if (fileSheet.value) {
    loading.value = true;
    processing.value.status = 'A carregar a planilha...';
    const formData = new FormData();
    formData.append('spreadsheet', fileSheet.value);
    try {
      const response = await axios.post('http://' + window.location.hostname + ':8000/api/preview', formData);
      previewRows.value = response.data.rows;
      selectedRows.value = response.data.rows.map(r => r.index);
    } catch (err) {
      console.error(err);
      message.value = "⚠️ Não foi possível pré-visualizar os nomes da planilha.";
      isError.value = true;
    } finally {
      loading.value = false;
      processing.value.status = '';
    }
  }
};

const selectAll = () => { selectedRows.value = previewRows.value.map(r => r.index); };
const deselectAll = () => { selectedRows.value = []; };

const generateDocs = async () => {
  loading.value = true;
  const totalDocs = selectedRows.value.length || previewRows.value.length;
  processing.value = { 
    current: 0, 
    total: totalDocs,
    status: `A preparar ${totalDocs} documento(s)...`
  };
  message.value = '';
  
  const formData = new FormData();
  formData.append('template', fileTemplate.value);
  formData.append('spreadsheet', fileSheet.value);
  formData.append('format_type', outputFormat.value);
  
  if (selectedRows.value.length > 0) {
    formData.append('selected_rows', JSON.stringify(selectedRows.value));
  }

  try {
    processing.value.status = 'A processar os documentos...';
    
    // Rota correta para a geração final
    const response = await axios.post(
      'http://' + window.location.hostname + ':8000/api/generate', 
      formData, 
      {
        responseType: 'blob',
        timeout: 600000, // 10 minutos de timeout
        onDownloadProgress: (event) => {
          if (event.total > 0) {
            processing.value.current = Math.ceil((event.loaded / event.total) * totalDocs);
            const percent = Math.round((event.loaded / event.total) * 100);
            processing.value.status = `A finalizar o download... ${percent}%`;
          }
        }
      }
    );

    processing.value.current = totalDocs;
    processing.value.status = '✅ Documentos prontos! Download iniciado...';

    // Trigger download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'FormSync_Documentos_Gerados.zip');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    message.value = `✅ Sucesso! ${totalDocs} documento(s) gerado(s).`;
    isError.value = false;
    
  } catch (err) {
    console.error('Erro na geração:', err);
    message.value = err.response?.data?.detail || "❌ Erro ao gerar os documentos. Verifica os ficheiros.";
    isError.value = true;
  } finally {
    loading.value = false;
    setTimeout(() => {
      processing.value = { current: 0, total: 0, status: '' };
    }, 3000);
  }
};
</script>
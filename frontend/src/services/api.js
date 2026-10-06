import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach Authorization header if token exists
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor to process standardized error messages
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let customError = 'An unexpected error occurred. Please try again.';
    
    if (error.response) {
      if (error.response.data && error.response.data.detail) {
        if (typeof error.response.data.detail === 'string') {
          customError = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          customError = error.response.data.detail.map(e => e.msg).join(', ');
        }
      }
    } else if (error.request) {
      customError = 'Unable to connect to backend server. Please check your connection.';
    }
    
    return Promise.reject(new Error(customError));
  }
);

// Health check helper
export const getHealthStatus = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

// BMI Service Helpers
export const calculateBMI = async (data) => {
  const response = await api.post('/api/bmi/calculate', data);
  return response.data;
};

export const getBMIHistory = async () => {
  const response = await api.get('/api/bmi/history');
  return response.data;
};

export const getLatestBMI = async () => {
  const response = await api.get('/api/bmi/latest');
  return response.data;
};

// Diabetes ML Prediction Service Helpers
export const predictDiabetes = async (data) => {
  const response = await api.post('/api/predictions/diabetes', data);
  return response.data;
};

export const getDiabetesHistory = async () => {
  const response = await api.get('/api/predictions/diabetes/history');
  return response.data;
};

export const getLatestDiabetesPrediction = async () => {
  const response = await api.get('/api/predictions/diabetes/latest');
  return response.data;
};

// Diabetes Complication ML Service Helpers
export const predictDiabetesComplications = async (data) => {
  const response = await api.post('/api/predictions/diabetes-complications', data);
  return response.data;
};

export const getLatestDiabetesComplicationPrediction = async () => {
  const response = await api.get('/api/predictions/diabetes-complications/latest');
  return response.data;
};

export const getDiabetesComplicationsHistory = async () => {
  const response = await api.get('/api/predictions/diabetes-complications/history');
  return response.data;
};

// Disease ML Prediction Service Helpers
export const predictDisease = async (data) => {
  const response = await api.post('/api/predictions/disease', data);
  return response.data;
};

export const getDiseaseHistory = async () => {
  const response = await api.get('/api/predictions/disease/history');
  return response.data;
};

export const getLatestDiseasePrediction = async () => {
  const response = await api.get('/api/predictions/disease/latest');
  return response.data;
};

export const getSupportedSymptoms = async () => {
  const response = await api.get('/api/predictions/disease/symptoms');
  return response.data;
};

// Health Risk Score Service Helpers
export const calculateHealthRisk = async () => {
  const response = await api.post('/api/health-risk/calculate');
  return response.data;
};

export const getLatestHealthRisk = async () => {
  const response = await api.get('/api/health-risk/latest');
  return response.data;
};

export const getHealthRiskHistory = async () => {
  const response = await api.get('/api/health-risk/history');
  return response.data;
};

// Diet Recommendation Service Helpers
export const createDietRecommendation = async (data) => {
  const response = await api.post('/api/recommendations/diet', data);
  return response.data;
};

export const getLatestDietRecommendation = async () => {
  const response = await api.get('/api/recommendations/diet/latest');
  return response.data;
};

export const getDietRecommendationHistory = async () => {
  const response = await api.get('/api/recommendations/diet/history');
  return response.data;
};

// Exercise Recommendation Service Helpers
export const createExerciseRecommendation = async (data) => {
  const response = await api.post('/api/recommendations/exercise', data);
  return response.data;
};

export const getLatestExerciseRecommendation = async () => {
  const response = await api.get('/api/recommendations/exercise/latest');
  return response.data;
};

export const getExerciseRecommendationHistory = async () => {
  const response = await api.get('/api/recommendations/exercise/history');
  return response.data;
};

// Medicine Reminder Service Helpers
export const createMedicineReminder = async (data) => {
  const response = await api.post('/api/medicines', data);
  return response.data;
};

export const getMedicineReminders = async () => {
  const response = await api.get('/api/medicines');
  return response.data;
};

export const getTodayMedicineReminders = async () => {
  const response = await api.get('/api/medicines/today');
  return response.data;
};

export const updateMedicineReminder = async (id, data) => {
  const response = await api.put(`/api/medicines/${id}`, data);
  return response.data;
};

export const deleteMedicineReminder = async (id) => {
  const response = await api.delete(`/api/medicines/${id}`);
  return response.data;
};

// Doctor & Appointment Service Helpers
export const getDoctors = async (specialization = '') => {
  const url = specialization ? `/api/doctors?specialization=${encodeURIComponent(specialization)}` : '/api/doctors';
  const response = await api.get(url);
  return response.data;
};

export const getDoctorById = async (id) => {
  const response = await api.get(`/api/doctors/${id}`);
  return response.data;
};

export const createAppointment = async (data) => {
  const response = await api.post('/api/appointments', data);
  return response.data;
};

export const getUserAppointments = async () => {
  const response = await api.get('/api/appointments');
  return response.data;
};

export const getNextUpcomingAppointment = async () => {
  const response = await api.get('/api/appointments/upcoming');
  return response.data;
};

export const updateAppointment = async (id, data) => {
  const response = await api.put(`/api/appointments/${id}`, data);
  return response.data;
};

export const cancelAppointment = async (id) => {
  const response = await api.delete(`/api/appointments/${id}`);
  return response.data;
};

// Health PDF Report Helper
export const downloadHealthReportPDF = async () => {
  const response = await api.get('/api/reports/health', {
    responseType: 'blob',
  });
  return response.data;
};

// Admin Service Helpers
export const getAdminDashboardStats = async () => {
  const response = await api.get('/api/admin/dashboard');
  return response.data;
};

export const getAdminPatients = async (search = '') => {
  const url = search ? `/api/admin/patients?search=${encodeURIComponent(search)}` : '/api/admin/patients';
  const response = await api.get(url);
  return response.data;
};

export const togglePatientStatus = async (patientId) => {
  const response = await api.put(`/api/admin/patients/${patientId}/toggle-status`);
  return response.data;
};

export const getAdminPredictions = async () => {
  const response = await api.get('/api/admin/predictions');
  return response.data;
};

export const getAdminAppointments = async () => {
  const response = await api.get('/api/admin/appointments');
  return response.data;
};

// Research & External Validation Service Helpers
export const getExternalValidationSummary = async () => {
  const response = await api.get('/api/v1/research/external-validation');
  return response.data;
};

export const getFairnessAnalysis = async () => {
  const response = await api.get('/api/v1/research/fairness-analysis');
  return response.data;
};

export const getCalibrationMetrics = async () => {
  const response = await api.get('/api/v1/research/calibration');
  return response.data;
};

export const getShapStability = async () => {
  const response = await api.get('/api/v1/research/shap-stability');
  return response.data;
};

export const getTripodAiReport = async () => {
  const response = await api.get('/api/v1/research/tripod-ai-report');
  return response.data;
};

export default api;

// frontend/src/store/slices/hcpSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const fetchHCPs = createAsyncThunk(
  'hcps/fetchAll',
  async () => {
    console.log('📡 Fetching HCPs from API...');
    const response = await api.get('/hcp');
    console.log('📥 API Response:', response.data);
    return response.data;
  }
);

export const createHCP = createAsyncThunk(
  'hcps/create',
  async (hcpData) => {
    const response = await api.post('/hcp', hcpData);
    return response.data;
  }
);

const hcpSlice = createSlice({
  name: 'hcps',
  initialState: {
    hcps: [],
    selectedHCP: null,
    loading: false,
    error: null,
  },
  reducers: {
    selectHCP: (state, action) => {
      state.selectedHCP = action.payload;
    },
    clearSelectedHCP: (state) => {
      state.selectedHCP = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHCPs.pending, (state) => {
        state.loading = true;
        state.error = null;
        console.log('⏳ Loading HCPs...');
      })
      .addCase(fetchHCPs.fulfilled, (state, action) => {
        state.loading = false;
        state.hcps = action.payload;
        console.log('✅ HCPs loaded:', state.hcps.length, 'HCPs');
      })
      .addCase(fetchHCPs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
        console.error('❌ Failed to fetch HCPs:', action.error.message);
      })
      .addCase(createHCP.pending, (state) => {
        state.loading = true;
      })
      .addCase(createHCP.fulfilled, (state, action) => {
        state.loading = false;
        state.hcps.push(action.payload);
        console.log('✅ HCP created:', action.payload.name);
      })
      .addCase(createHCP.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
        console.error('❌ Failed to create HCP:', action.error.message);
      });
  },
});

export const { selectHCP, clearSelectedHCP } = hcpSlice.actions;
export default hcpSlice.reducer;
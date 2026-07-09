import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const logInteraction = createAsyncThunk(
  'interactions/log',
  async (interactionData) => {
    const response = await api.post('/interactions', interactionData);
    return response.data;
  }
);

export const fetchInteractions = createAsyncThunk(
  'interactions/fetchAll',
  async () => {
    const response = await api.get('/interactions');
    return response.data;
  }
);

export const fetchHCPInteractions = createAsyncThunk(
  'interactions/fetchHCP',
  async (hcpId) => {
    const response = await api.get(`/interactions/hcp/${hcpId}`);
    return response.data;
  }
);

const interactionSlice = createSlice({
  name: 'interactions',
  initialState: {
    interactions: [],
    currentInteraction: null,
    loading: false,
    error: null,
  },
  reducers: {
    setCurrentInteraction: (state, action) => {
      state.currentInteraction = action.payload;
    },
    clearCurrentInteraction: (state) => {
      state.currentInteraction = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(logInteraction.pending, (state) => {
        state.loading = true;
      })
      .addCase(logInteraction.fulfilled, (state, action) => {
        state.loading = false;
        state.interactions.unshift(action.payload);
        state.currentInteraction = action.payload;
      })
      .addCase(logInteraction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(fetchInteractions.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.loading = false;
        state.interactions = action.payload;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(fetchHCPInteractions.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchHCPInteractions.fulfilled, (state, action) => {
        state.loading = false;
        state.interactions = action.payload;
      })
      .addCase(fetchHCPInteractions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { setCurrentInteraction, clearCurrentInteraction } = interactionSlice.actions;
export default interactionSlice.reducer;
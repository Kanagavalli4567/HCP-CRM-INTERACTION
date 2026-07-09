// src/store/index.js
import { configureStore } from '@reduxjs/toolkit'
import interactionReducer from './slices/interactionSlice'
import hcpReducer from './slices/hcpSlice'

export const store = configureStore({
  reducer: {
    interactions: interactionReducer,
    hcps: hcpReducer,
  },
})
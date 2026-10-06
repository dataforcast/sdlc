import axios, { type AxiosRequestConfig } from 'axios';

// In the browser (Vite dev server, relative requests proxied to the backend),
// leave the base URL empty. Outside the browser (Orval generation is a separate
// concern; this covers the Node-based integration test), fall back to
// process.env.API_BASE_URL, a full origin.
const baseURL =
  (import.meta as unknown as { env?: Record<string, string> }).env?.VITE_API_BASE_URL ??
  (typeof process !== 'undefined' ? process.env.API_BASE_URL : undefined) ??
  '';

const axiosInstance = axios.create({ baseURL });

export const apiClient = <T>(config: AxiosRequestConfig): Promise<T> =>
  axiosInstance(config).then((response) => response.data);

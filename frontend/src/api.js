import axios from "axios";

// In production, the backend serves the frontend, so use relative URLs
// In development, use the local backend URL
const API_BASE = import.meta.env.VITE_API_URL || (
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : window.location.origin
);

const api = axios.create({
  baseURL: API_BASE,
});
export const axiosInstance = api;
export { API_BASE };

export const startCampaign = async () => {
  const { data } = await api.post("/start-campaign");
  return data;
};

export const startDevCampaign = async () => {
  const { data } = await api.post("/dev-start");
  return data;
};

export const submitAnswer = async (sessionId, answer) => {
  const { data } = await api.post(`/submit-answer/${sessionId}`, { answer });
  return data;
};

export const getStatus = async (sessionId) => {
  const { data } = await api.get(`/status/${sessionId}`);
  return data;
};

export const exportVariant = async (sessionId, themeName, ratioId, heading, content, catchyLine, bp, bs, bt) => {
  const { data } = await api.get(`/render-single`, {
    params: {
        session_id: sessionId,
        theme_name: themeName,
        ratio_id: ratioId,
        heading: heading,
        content: content,
        catchy_line: catchyLine,
        bp, bs, bt
    }
  });
  return data;
};

export const exportPack = async (sessionId, themeName, heading, content, catchyLine, bp, bs, bt) => {
  const { data } = await api.get(`/export-pack`, {
    params: {
        session_id: sessionId,
        theme_name: themeName,
        heading: heading,
        content: content,
        catchy_line: catchyLine,
        bp, bs, bt
    }
  });
  return data;
};

export const exportGlobal = async (sessionId, themeName, heading, content, catchyLine, bp, bs, bt) => {
  const { data } = await api.get(`/export-global`, {
    params: {
        session_id: sessionId,
        theme_name: themeName,
        heading: heading,
        content: content,
        catchy_line: catchyLine,
        bp, bs, bt
    }
  });
  return data;
};

export const transcreatePreview = async (sessionId, heading, content, catchyLine, targetLang) => {
  const { data } = await api.get(`/transcreate-preview`, {
    params: {
        session_id: sessionId,
        heading: heading,
        content: content,
        catchy_line: catchyLine,
        target_lang: targetLang
    }
  });
  return data;
};

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // 백엔드(FastAPI) 개발 서버로 /api 요청 전달
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
});

import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".");
  return {
    plugins: [react()],
    server: {
      // 백엔드(FastAPI)로 /api 요청 전달. VITE_API_TARGET으로 변경 가능
      proxy: { "/api": env.VITE_API_TARGET || "http://127.0.0.1:8000" },
    },
  };
});

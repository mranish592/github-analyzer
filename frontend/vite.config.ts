import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig, loadEnv } from "vite"

// // https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
      define: {
          "process.env.REACT_APP_API_BASE_URL": JSON.stringify(env.REACT_APP_API_BASE_URL),
      },
      plugins: [react(), tailwindcss()],
      resolve: {
          alias: {
              "@": path.resolve(__dirname, "./src"),
          },
      },
  };
});
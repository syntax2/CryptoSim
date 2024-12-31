const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = function (app) {
  app.use(
    "/api",
    createProxyMiddleware({
      target: "http://worker:8002",
      changeOrigin: true,
      pathRewrite: {
        "^/api": "/", // Remove /api prefix when forwarding to worker
      },
    })
  );
};

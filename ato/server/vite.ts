import express, { type Express } from "express";
import { Server } from "http";
import path from "path";

export function log(...args: any[]) {
  console.log("[server]", ...args);
}

export async function setupVite(app: Express, server: Server) {
  // Đây là triển khai đơn giản cho môi trường phát triển
  log("Setting up vite dev environment");
  app.get("*", (_req, res) => {
    res.sendFile(path.resolve("./client/index.html"));
  });
  
  return server;
}

export function serveStatic(app: Express) {
  // Đây là hàm phục vụ tệp tĩnh cho môi trường sản xuất
  log("Setting up static file serving");
  app.use(express.static("./client/dist"));
  
  app.get("*", (_req, res) => {
    res.sendFile(path.resolve("./client/dist/index.html"));
  });
}
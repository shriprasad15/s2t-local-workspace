import {
  CopilotRuntime,
  OpenAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { NextRequest } from "next/server";
import OpenAI from "openai";

// Create OpenAI client with DOSASHOP API configuration
const openai = new OpenAI({
  apiKey: "dummy-key", // Required by OpenAI client but not used by DOSASHOP
  baseURL: process.env.OPENAI_BASE_URL || process.env.DOSASHOP_URL || "https://api.dosashop1.com/openai/v1",
  defaultHeaders: {
    "api-key": process.env.DOSASHOP_API_KEY || "4e36ea7193b64a799d3f169cd9d01f3a",
  },
});

// Create service adapter with DOSASHOP configuration and CSV context
const serviceAdapter = new OpenAIAdapter({
  openai,
  model: "gpt-4o",
});

// Create the CopilotRuntime instance
const runtime = new CopilotRuntime();

// Build a Next.js API route that handles the CopilotKit runtime requests
export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};
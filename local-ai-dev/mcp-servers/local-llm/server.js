import express from "express";
import bodyParser from "body-parser";
import fetch from "node-fetch";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(bodyParser.json());

const PROVIDER = process.env.LLM_PROVIDER; // ollama | openai
const BASE_URL = process.env.LLM_BASE_URL;
const MODEL = process.env.LLM_MODEL;
const PORT = 3005;

async function callLLM(prompt) {
  if (PROVIDER === "ollama") {
    const res = await fetch(`${BASE_URL}/api/generate`, {
      method: "POST",
      body: JSON.stringify({
        model: MODEL,
        prompt,
      }),
    });
    const json = await res.json();
    return json.response;
  }

  if (PROVIDER === "openai") { // For LM Studio (OpenAI compatible)
    const res = await fetch(`${BASE_URL}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: MODEL,
        messages: [{ role: "user", content: prompt }],
        temperature: 0.2,
      }),
    });
    const json = await res.json();
    return json.choices[0].message.content;
  }

  return "No valid LLM provider configured. Please check your .env file.";
}

app.post("/run", async (req, res) => {
  const prompt = req.body.prompt || "";
  const result = await callLLM(prompt);
  res.json({ result });
});

app.listen(PORT, () => {
  console.log(`Local LLM MCP server running on port ${PORT}`);
  console.log(`LLM Provider: ${PROVIDER}`);
  console.log(`LLM Base URL: ${BASE_URL}`);
  console.log(`LLM Model: ${MODEL}`);
});
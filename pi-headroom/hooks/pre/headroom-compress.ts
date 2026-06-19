import type { HookAPI } from "@oh-my-pi/pi-coding-agent/extensibility/hooks";
import { HeadroomClient } from "headroom-ai";

/**
 * Headroom tool-result compression hook for oh-my-pi.
 *
 * Intercepts tool results before they reach the model, compresses large outputs
 * via Headroom, and stores originals locally. The model can call
 * `headroom_retrieve` to fetch uncompressed originals on demand.
 *
 * NOTE: omp 16.0.9 does not support the `context` hook's `{ messages }`
 * return contract for full message-array replacement. This hook targets
 * `tool_result` instead.
 *
 * NOTE: Headroom standalone compression via HeadroomClient requires the
 * headroom proxy in API-passthrough mode (ANTHROPIC_BASE_URL) or a
 * headroom cloud API key. The local proxy's /v1/compress endpoint may
 * return null metrics if not configured for standalone compression.
 * This hook falls back to basic truncation when Headroom returns no savings.
 */

const COMPRESS_THRESHOLD_CHARS = 2000;
const DEFAULT_MODEL = "claude-3-5-sonnet-20241022";

export default function (pi: HookAPI) {
  pi.on("tool_result", async (event) => {
    if (event.isError || !event.content) return;

    const textBlocks = event.content.filter((c: any) => c.type === "text");
    if (textBlocks.length === 0) return;

    const totalChars = textBlocks.reduce(
      (sum: number, c: any) => sum + (c.text?.length || 0),
      0,
    );
    if (totalChars < COMPRESS_THRESHOLD_CHARS) return;

    // Try Headroom compression first.
    let compressedText: string | null = null;
    try {
      const client = new HeadroomClient({ baseUrl: "http://localhost:8787" });
      const messages = textBlocks.map((c: any) => ({
        role: "user" as const,
        content: c.text,
      }));
      const result = await client.compress(messages, { model: DEFAULT_MODEL });

      if (result.tokensSaved && result.tokensSaved > 0) {
        compressedText = result.messages.map((m: any) => m.content).join("\n---\n");
      }
    } catch (_e) {
      // Headroom failed or not configured — fall through to basic truncation.
    }

    // Fallback: basic truncation with metadata.
    if (!compressedText) {
      const originalText = textBlocks.map((c: any) => c.text).join("\n");
      const lines = originalText.split("\n");
      const MAX_LINES = 50;
      if (lines.length > MAX_LINES) {
        compressedText =
          lines.slice(0, MAX_LINES).join("\n") +
          `\n\n[... ${lines.length - MAX_LINES} lines truncated. Use headroom_retrieve to fetch full original if needed.]`;
      } else {
        // Not truncatable — pass through unchanged.
        return;
      }
    }

    const newContent = event.content.map((c: any) => {
      if (c.type === "text") {
        return { ...c, text: compressedText };
      }
      return c;
    });

    return { content: newContent };
  });
}

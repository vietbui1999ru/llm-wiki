import type { CustomToolFactory } from "@oh-my-pi/pi-coding-agent";
import { HeadroomClient } from "headroom-ai";

/**
 * Headroom retrieval tool for oh-my-pi.
 *
 * When the `headroom-compress` hook runs, CCR stores the original uncompressed
 * messages locally and returns compressed surrogates. If the model needs details
 * that were summarized away, it calls `headroom_retrieve` with the chunk ID
 * embedded in the compressed message.
 */

const factory: CustomToolFactory = (pi) => ({
  name: "headroom_retrieve",
  label: "Headroom Retrieve",
  description:
    "Retrieve the original uncompressed content for a compressed message chunk. " +
    "Use when you need details that were summarized or compressed away. " +
    "The chunkId is embedded in compressed message metadata.",
  parameters: pi.zod.object({
    chunkId: pi.zod
      .string()
      .describe("The ID of the compressed chunk to retrieve (from message metadata)"),
  }),

  async execute(_toolCallId, params, onUpdate, _ctx, _signal) {
    onUpdate?.({
      content: [
        {
          type: "text",
          text: `Retrieving original for chunk ${params.chunkId}...`,
        },
      ],
    });

    const client = new HeadroomClient();
    const result = await client.retrieve(params.chunkId);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
      details: {
        chunkId: params.chunkId,
        result,
      },
    };
  },
});

export default factory;

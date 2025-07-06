# agent_3.py

from mcp.message_protocol import MCPMessage
import together
import os

class LLMResponseAgent:
    def __init__(self, name="LLMResponseAgent"):
        self.name = name
        together.api_key = "00cdccaa2ec759d498e67055abd0f051bffdb132ebb516f241dd37156b3aa0da"  # Make sure this is set in your environment
        self.model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

    def build_prompt(self, query, context_chunks):
        context = "\n".join(context_chunks)
        return f"""
You are an AI assistant. Return only the answer related to the user's query: '{query}' from the provided context.
Ignore any unrelated content such as test cases, thank you notes, or page numbers.

Context:
{context}

Question: {query}
Answer:
"""

    def handle_context(self, mcp_message):
        query = mcp_message.payload["query"]
        context_chunks = mcp_message.payload["retrieved_context"]
        trace_id = mcp_message.trace_id

        prompt = self.build_prompt(query, context_chunks)

        # ✅ Log the full prompt being sent
        print("\n📤 Prompt sent to TogetherAI:")
        print(prompt)

        try:
            response = together.Complete.create(
                prompt=prompt,
                model=self.model,
                max_tokens=200,
                temperature=0.3,
                stop=["</s>", "Question:"]
            )

            answer = response['choices'][0]['text'].strip()
        except Exception as e:
            answer = f"[LLM Error] {str(e)}"

        result_msg = MCPMessage(
            sender=self.name,
            receiver="UI",
            msg_type="ANSWER_RESPONSE",
            trace_id=trace_id,
            payload={
                "answer": answer,
                "sources": context_chunks
            }
        )

        print(f"\n[{result_msg.sender} ➜ {result_msg.receiver}] {result_msg.to_dict()}")
        return result_msg

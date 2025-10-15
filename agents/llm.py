# agents/llm.py

from mcp.message_protocol import MCPMessage
import together
import os

class LLMResponseAgent:
    def __init__(self, name="LLMResponseAgent"):
        self.name = name  # Agent identifier
        # Set up Together.AI API key (should use environment variable in production)
        together.api_key = "00cdccaa2ec759d498e67055abd0f051bff32ebb516f241dd37156b3aa0da"
        # Use free Llama model for responses
        self.model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

    def build_prompt(self, query, context_chunks):
        """
        Create a well-structured prompt for the LLM
        Args:
            query: User's question
            context_chunks: Relevant text chunks from retrieval
        Returns:
            Formatted prompt string
        """
        # Join all context chunks into one text block
        context = "\n".join(context_chunks)
        
        # Create a clear prompt with instructions
        return f"""
You are an AI assistant. Return only the answer related to the user's query: '{query}' from the provided context.
Ignore any unrelated content such as test cases, thank you notes, or page numbers.

Context:
{context}

Question: {query}
Answer:
"""

    def handle_context(self, mcp_message):
        """
        Generate answer using LLM based on retrieved context
        Args:
            mcp_message: Message containing query and context
        Returns:
            Message with generated answer
        """
        # Extract information from message
        query = mcp_message.payload["query"]
        context_chunks = mcp_message.payload["retrieved_context"]
        trace_id = mcp_message.trace_id

        # Build the prompt for LLM
        prompt = self.build_prompt(query, context_chunks)

        # Log the prompt being sent (helpful for debugging)
        print("\n📤 Prompt sent to TogetherAI:")
        print(prompt)

        try:
            # Call Together.AI API to generate response
            response = together.Complete.create(
                prompt=prompt,
                model=self.model,
                max_tokens=200,        # Limit response length
                temperature=0.3,       # Low creativity for factual answers
                stop=["</s>", "Question:"]  # Stop tokens to end generation
            )

            # Extract the generated text
            answer = response['choices'][0]['text'].strip()
        except Exception as e:
            # Handle API errors gracefully
            answer = f"[LLM Error] {str(e)}"

        # Create response message for UI
        result_msg = MCPMessage(
            sender=self.name,
            receiver="UI",
            msg_type="ANSWER_RESPONSE",
            trace_id=trace_id,
            payload={
                "answer": answer,
                "sources": context_chunks  # Include sources for transparency
            }
        )

        print(f"\n[{result_msg.sender} ➜ {result_msg.receiver}] {result_msg.to_dict()}")
        return result_msg

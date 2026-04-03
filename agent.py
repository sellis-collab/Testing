"""
Web Researcher Agent
--------------------
Uses the Claude Agent SDK to research a topic using WebSearch and WebFetch,
then returns a concise summary.
"""

import anyio
import sys
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage, TextBlock


async def research(topic: str) -> str:
    """Run the web researcher agent on a given topic."""
    print(f"\nResearching: {topic}\n{'=' * 50}")

    async for message in query(
        prompt=(
            f"Research the following topic and provide a clear, well-structured summary "
            f"with key facts, recent developments, and any notable sources:\n\n{topic}"
        ),
        options=ClaudeAgentOptions(
            allowed_tools=["WebSearch", "WebFetch"],
        ),
    ):
        # Stream assistant text as it arrives
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)

        # ResultMessage signals the agent is done
        if isinstance(message, ResultMessage):
            print()  # newline after streamed output
            return message.result

    return ""


async def main() -> None:
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "latest developments in AI agents"
    await research(topic)


if __name__ == "__main__":
    anyio.run(main)

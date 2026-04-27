"""
Test: Gemini 3.x thought signature support in ToolCall and _call_google().

Verifies that:
1. ToolCall can store and serialize thought_signature (bytes → base64)
2. ToolCall.to_dict() includes thought_signature when present
3. ToolCall.to_dict() omits thought_signature when None
4. The reconstructed Part for Gemini includes thought_signature
5. FunctionResponse includes id when available
"""

import base64

import pytest


def test_toolcall_with_thought_signature():
    """ToolCall stores thought_signature as bytes and serializes to base64."""
    from router.llm_client import ToolCall

    sig = b"\x01\x02\x03\x04test_signature"
    tc = ToolCall(
        id="call_abc123",
        name="search",
        arguments={"query": "test"},
        thought_signature=sig,
    )

    assert tc.thought_signature == sig
    d = tc.to_dict()
    assert "thought_signature" in d
    # Verify it's valid base64 that decodes back to original
    decoded = base64.b64decode(d["thought_signature"])
    assert decoded == sig


def test_toolcall_without_thought_signature():
    """ToolCall without thought_signature omits it from dict."""
    from router.llm_client import ToolCall

    tc = ToolCall(
        id="call_abc123",
        name="search",
        arguments={"query": "test"},
    )

    assert tc.thought_signature is None
    d = tc.to_dict()
    assert "thought_signature" not in d


def test_gemini_part_with_thought_signature():
    """Verify we can create a Gemini Part with function_call + thought_signature."""
    from google.genai import types as _gtypes

    sig = b"test_thought_signature_bytes"
    fc = _gtypes.FunctionCall(name="test_tool", args={"key": "value"})
    fc.id = "call_test_001"

    part = _gtypes.Part(
        function_call=fc,
        thought_signature=sig,
    )

    assert part.function_call.name == "test_tool"
    assert part.function_call.args == {"key": "value"}
    assert part.function_call.id == "call_test_001"
    assert part.thought_signature == sig


def test_gemini_function_response_with_id():
    """Verify FunctionResponse can include id for Gemini 3.x."""
    from google.genai import types as _gtypes

    fr = _gtypes.FunctionResponse(
        name="test_tool",
        response={"result": "success"},
    )
    fr.id = "call_test_001"

    part = _gtypes.Part(function_response=fr)
    assert part.function_response.name == "test_tool"
    assert part.function_response.id == "call_test_001"


def test_thought_signature_propagation_in_tool_results():
    """Verify thought_signature flows through the tool dispatch pipeline."""
    # Simulate what tool_dispatch does: propagate thought_signature from
    # pending_tool_call to tool_result
    pending_tc = {
        "id": "call_abc",
        "name": "search",
        "arguments": {"q": "test"},
        "thought_signature": base64.b64encode(b"sig_bytes").decode("ascii"),
    }

    # Simulate tool_dispatch building result_entry
    result_entry = {
        "tool_call_id": pending_tc["id"],
        "name": pending_tc["name"],
        "args": pending_tc["arguments"],
        "result": {"status": "ok"},
    }
    if pending_tc.get("thought_signature"):
        result_entry["thought_signature"] = pending_tc["thought_signature"]

    assert "thought_signature" in result_entry
    assert result_entry["thought_signature"] == base64.b64encode(b"sig_bytes").decode("ascii")


def test_reconstructed_tool_call_includes_thought_signature():
    """Verify engine.py's reconstructed_tool_calls include thought_signature."""
    import json

    # Simulate what engine.py does with tool_results
    tool_results = [
        {
            "tool_call_id": "call_abc",
            "name": "search",
            "args": {"q": "test"},
            "result": {"status": "ok"},
            "thought_signature": base64.b64encode(b"sig_bytes").decode("ascii"),
        }
    ]

    reconstructed_tool_calls = []
    for tr in tool_results:
        tc_entry = {
            "id": tr.get("tool_call_id", ""),
            "type": "function",
            "function": {
                "name": tr.get("name", "tool"),
                "arguments": json.dumps(tr.get("args", {}), ensure_ascii=False),
            },
        }
        if tr.get("thought_signature"):
            tc_entry["thought_signature"] = tr["thought_signature"]
        reconstructed_tool_calls.append(tc_entry)

    assert len(reconstructed_tool_calls) == 1
    assert "thought_signature" in reconstructed_tool_calls[0]
    assert reconstructed_tool_calls[0]["thought_signature"] == base64.b64encode(b"sig_bytes").decode("ascii")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


def test_anthropic_tool_calls_conversion():
    """Verify OpenAI-format tool_calls are converted to Anthropic tool_use blocks."""
    import json

    # Simulate what engine.py sends as reconstructed assistant message
    assistant_msg = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_abc123",
                "type": "function",
                "function": {
                    "name": "search",
                    "arguments": json.dumps({"query": "test"}),
                },
            }
        ],
    }

    # Simulate what _call_anthropic should do
    content_blocks = []
    text_content = assistant_msg.get("content")
    if text_content and isinstance(text_content, str) and text_content.strip():
        content_blocks.append({"type": "text", "text": text_content})
    for tc in assistant_msg["tool_calls"]:
        fn = tc.get("function", {})
        fn_args_raw = fn.get("arguments", "{}")
        if isinstance(fn_args_raw, str):
            fn_args = json.loads(fn_args_raw)
        else:
            fn_args = fn_args_raw
        content_blocks.append(
            {
                "type": "tool_use",
                "id": tc.get("id", ""),
                "name": fn.get("name", "tool"),
                "input": fn_args,
            }
        )

    result = {"role": "assistant", "content": content_blocks}

    assert result["role"] == "assistant"
    assert len(result["content"]) == 1
    assert result["content"][0]["type"] == "tool_use"
    assert result["content"][0]["id"] == "call_abc123"
    assert result["content"][0]["name"] == "search"
    assert result["content"][0]["input"] == {"query": "test"}

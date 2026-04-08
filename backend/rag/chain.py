from openai import OpenAI

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based only on the provided context.
If the context does not contain enough information to answer the question, say so clearly.
Do not make up information that is not supported by the context.

Context:
{context}"""


def generate_answer(
    question: str,
    contexts: list[str],
    model: str,
    api_key: str,
) -> dict:
    """Generate an answer using the given contexts and model.

    Returns dict with 'answer', 'token_count', 'model'.
    """
    client = OpenAI(api_key=api_key)
    context_text = "\n\n---\n\n".join(contexts)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context_text)},
            {"role": "user", "content": question},
        ],
        temperature=0.1,
    )

    usage = response.usage
    return {
        "answer": response.choices[0].message.content,
        "token_count": usage.total_tokens if usage else 0,
        "model": model,
    }

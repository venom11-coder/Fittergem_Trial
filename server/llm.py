

import os 
from openai import OpenAI






def query_openai(
    query: str
) -> str:
    """Send a query to GROK's grok-3-mini with context.

    Args:
        query: The user's question

    Returns:
        str: The AI's response, or an error message if the query fails.
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not client.api_key:
            return "Error: No OPENAI API key found. Set OPENAI_API_KEY in .env"

        # Build context messages from long-term memory
        messages = []

        messages.append(
            {"role": "system", "content": "You are a personal assistant. The user is asking you a question. Answer briefly and concisely. If one sentence is enough, answer with one sentence. "},
        )    

 
        # Add user query
        messages.append({"role": "user", "content": query})

        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=messages
        )


        # Extract and return the AI's response
        if response.choices and response.choices[0].message:
            ai_content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason

            if ai_content is not None:
                #logging.info("Received response content from GROK.")
                return ai_content
            else:

                return f"Error querying AI: OPENAI response message content is None. Finish reason: {finish_reason}."
        else:
            return "Error querying AI: No choices or message object returned from OPENAI."

    except Exception as e:
        #logging.error(f"Error querying GROK: {e}", exc_info=True)
        return f"Error querying AI: {str(e)}"


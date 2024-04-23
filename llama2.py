import ollama

def gen_response(message1):
    stream = ollama.chat(
        model='llama2',
        messages=[{'role': 'user', 'content': message1}],
        stream=True,
    )
    response= ""
    for chunk in stream:
        #print(chunk['message']['content'], end='', flush=True)
        response += chunk['message']['content']
    #response=message
    print("this is the output from llama2 file", response)
    return response
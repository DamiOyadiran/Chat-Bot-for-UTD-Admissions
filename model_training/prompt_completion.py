import openai, embedded_context, os, pandas as pd

MAX_SEC_LEN = 1000
SEPARATOR = "\n* "

DF = pd.read_csv(os.path.join(os.path.dirname(__file__), 'tabled_data_with_answers_2.csv'))

def format(input):
    # Stuff done that we'll figure out to maximalize its accuracy for the model

    # Remove last question-answer pairing from the context
    #if (len(context_array) > max_context):
        #context_array = context_array[2:]
    #context_array.append(input)

   # model_completion_prompt = create_question()

    top_context = embedded_context.find_context(input)

    chosen_sections = []
    sects_len = 0
    sects_indices = []

    for _, section_index in top_context:
        document_section = DF.loc[DF['title'] == section_index[1]].values
        sects_len += document_section[0][3]
        if sects_len > MAX_SEC_LEN:
            break

        chosen_sections.append(SEPARATOR + document_section[0][2].replace("\n", " "))
        sects_indices.append(str(section_index))

    model_completion_prompt = """Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, say "I don't know." The answer should end in a complete sentence with a period.\n\nContext:\n"""
    model_completion_prompt += "".join(chosen_sections) + "\n\n Q: " + input + "\n A:"
    print(model_completion_prompt)
    
    output = model_completion(model_completion_prompt)
    

    return output

def model_completion(input):
    return openai.Completion.create(
        model='ada',
        prompt=input,
        echo=False,
        stop='\n',
        max_tokens=50
    )
#:ft-cs-chatbot-t5-2023-03-09-03-56-59

def create_question():
    messages = [{"role": "system", "content": "You are a system made to create a question based off of the prior conversation."}]

    i = 0
    while (i < len(context_array) - 1):
        messages.append({"role": "user", "content": context_array[i]})
        messages.append({"role": "assistant", "content": context_array[i+1]})
        i += 2

    messages.append({"role": "user", "content": context_array[i]}) # Newest message provided by the user
    messages.append({"role": "user", "content": "Create a question based off the previous conversation we have had, or if there is only one previous question, turn it into a question if it is not already one."})

    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )['choices'][0]['message']['content']

# Testing without util of front-end
if __name__ == "__main__":
    while (True):
        user_prompt = input("Provide user input: ")
        if (user_prompt == "exit"):
            break

        print(format(user_prompt))
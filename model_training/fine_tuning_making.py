from sklearn.model_selection import train_test_split
import pandas as pd, os, embedded_context, random, time

FILE = './formatted_data/data_set_with_answers_full.csv'
DF = pd.read_csv(os.path.join(os.path.dirname(__file__), FILE))

train_df, test_df = train_test_split(DF, test_size=0.2, random_state=42)

# Get a random context that isn't the best fit for answering the question
def get_other_contexts(question, chosen_context):
    context_array = embedded_context.find_context(question)[:4]

    candidates = []
    for _, context_title in context_array:
        context = DF.loc[DF['title'] == context_title[1]].values[0][2]

        if (context == chosen_context):
            continue
        candidates.append(context)

        return random.choice(candidates)

def create_tuning_set(df, discrim=False):
    num_iterations = 0

    rows = []
    df = df[df.questions > " "] # Removing bad rows from the dataframe (surprisingly simple!)
    for i, row in df.iterrows():
        for q, a in zip(("1." + row.questions).split('\n'), ("1." + row.answers).split('\n')):
            if discrim:
                rows.append({"prompt":f"{row.context}\nQuestion: {q[2:].strip()}\n Related:", "completion":f" yes"})
            else:
                rows.append({"prompt":f"{row.context}\nQuestion: {q[2:].strip()}\nAnswer:", "completion":f" {a[2:].strip()}"})
# rate limits make me cry :(
        for q in ("1." + row.questions).split('\n'):
            for j in range(3): # In addition to the main context, we'll want to get other wrong contexts to train the model on incorrect responses
                random_context = ""
                if j == 0:
                    subset = df[(df.topic == row.topic) & (df.context != row.context)]
                    if len(subset) < 1:
                            continue
                    random_context = subset.sample(1).iloc[0].context # just grab any one context from the DF

                elif j == 1:
                    if (num_iterations != 0 and num_iterations % 30 == 0):
                        print(f'sleep {num_iterations / 30 + 1} started')
                        time.sleep(90) # Getting around rate limiting :/
                        print(f'sleep {num_iterations / 30 + 1} completed')
                    random_context = get_other_contexts(q[2:].strip(), row.context)
                    num_iterations += 1

                else:
                    while (True):
                        random_context = df.sample(1).iloc[0].context
                        if random_context != row.context:
                            break

            if discrim:
                rows.append({"prompt":f"{random_context}\nQuestion: {q[2:].strip()}\n Related:", "completion":f" no"})
            else:
                rows.append({"prompt":f"{random_context}\nQuestion: {q[2:].strip()}\nAnswer:", "completion":f" No appropriate context found."})

    return pd.DataFrame(rows)

# Creating both a testing and training set to ensure the accuracy of our created models
for name, is_disc in [('discriminator', True), ('qa', False)]:
    for train_test, dt in [('train', train_df), ('test', test_df)]:
        ft = create_tuning_set(dt, is_disc)
        ft.to_json(f'{name}_{train_test}.jsonl', orient='records', lines=True)
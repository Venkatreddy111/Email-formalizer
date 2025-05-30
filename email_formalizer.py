# -*- coding: utf-8 -*-
"""email formalizer.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zSTpj-btEb8rfrJX8Uj9c9Oq7BXNuZ8L
"""

!pip install -q transformers datasets evaluate sacrebleu

import pandas as pd
from datasets import Dataset
from transformers import T5Tokenizer, T5ForConditionalGeneration, TrainingArguments, Trainer, DataCollatorForSeq2Seq
import evaluate
import numpy as np

df = pd.read_csv("/content/email_formalizer_5000.csv")[["input_text", "target_text"]].dropna()

df.head()

df = df.rename(columns={"input_text": "informal_text", "target_text": "formal_text"})

df = df.sample(n=5000, random_state=42) if len(df) > 5000 else df

dataset = Dataset.from_pandas(df)
dataset = dataset.train_test_split(test_size=0.1)
train_ds = dataset["train"]
test_ds = dataset["test"]

tokenizer = T5Tokenizer.from_pretrained("t5-small")

def preprocess_function(examples):
    inputs = ["formalize: " + text for text in examples["informal_text"]]
    model_inputs = tokenizer(inputs, max_length=128, truncation=True, padding="max_length")
    labels = tokenizer(examples["formal_text"], max_length=128, truncation=True, padding="max_length")
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_train = train_ds.map(preprocess_function, batched=True)
tokenized_test = test_ds.map(preprocess_function, batched=True)

model = T5ForConditionalGeneration.from_pretrained("t5-small")

bleu = evaluate.load("sacrebleu")

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    result = bleu.compute(predictions=decoded_preds, references=[[label] for label in decoded_labels])
    return {"bleu": result["score"]}

training_args = TrainingArguments(
    output_dir="./t5-email-formalizer",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    logging_dir="./logs",
    logging_steps=10,
    save_total_limit=1,
    save_steps=500
)

data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

trainer.train()

def formalize_email(text):
    input_ids = tokenizer("formalize: " + text, return_tensors="pt", padding=True, truncation=True).input_ids
    output_ids = model.generate(input_ids, max_length=128, num_beams=4, early_stopping=True)
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)

# Sample Inputs
examples = [
    "sorry I can't make it to the meeting",
    "got ur msg. will reply soon",
    "hey, send me the file asap!",
    "can't attend class today, not feeling well"
]

for text in examples:
    print(f"Informal: {text}")
    print(f"Formal  : {formalize_email(text)}\n")

model.save_pretrained("/content/t5-email-formalizer")
tokenizer.save_pretrained("/content/t5-email-formalizer")

from google.colab import files
!zip -r t5-email-formalizer.zip t5-email-formalizer
files.download("t5-email-formalizer.zip")

df.to_csv("email_formalizer_used.csv", index=False)
files.download("email_formalizer_used.csv")

!unzip t5-email-formalizer.zip

from transformers import T5ForConditionalGeneration, T5Tokenizer

model = T5ForConditionalGeneration.from_pretrained("/content/t5-email-formalizer")
tokenizer = T5Tokenizer.from_pretrained("/content/t5-email-formalizer")

def formalize_email(informal_text):
    input_text = "formalize: " + informal_text
    input_ids = tokenizer.encode(input_text, return_tensors="pt", truncation=True)
    output_ids = model.generate(input_ids, max_length=128, num_beams=4, early_stopping=True)
    formal_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return formal_text

# Example informal text
informal = "sorry i cant come to the meeting"
formal = formalize_email(informal)
print("Formal Email:\n", formal)

from transformers import T5ForConditionalGeneration, T5Tokenizer

model_path = "./t5-email-formalizer"  # or the path where you saved the model
model = T5ForConditionalGeneration.from_pretrained(model_path)
tokenizer = T5Tokenizer.from_pretrained(model_path)

!pip install streamlit pyngrok

!ngrok config add-authtoken 2woKgI9d2dNLwtAsKbqQWeqPA7b_2P9RL9hZe6Pb2Gs5QroF

# Commented out IPython magic to ensure Python compatibility.
# %%writefile app.py
# import streamlit as st
# from transformers import T5ForConditionalGeneration, T5Tokenizer
# 
# @st.cache_resource
# def load_model():
#     model = T5ForConditionalGeneration.from_pretrained("./t5-email-formalizer")
#     tokenizer = T5Tokenizer.from_pretrained("./t5-email-formalizer")
#     return model, tokenizer
# 
# model, tokenizer = load_model()
# 
# st.title("📧 Email Formalizer")
# input_text = st.text_area("Enter informal email/text:", height=150)
# 
# if st.button("Formalize"):
#     input_ids = tokenizer.encode("formalize: " + input_text, return_tensors="pt", truncation=True)
#     outputs = model.generate(input_ids, max_length=128, num_beams=4, early_stopping=True)
#     formal_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     st.success("Formalized Output:")
#     st.write(formal_output)
#

# Run Streamlit
import os
os.system('streamlit run app.py &')

# Connect ngrok
from pyngrok import ngrok
public_url = ngrok.connect(addr=8501, proto="http")
print("🔗 Streamlit app is live at:", public_url)

!git config --global user.name "Venkatreddy111"
!git config --global user.email "venkatreddypasam4@gmail.com"

!git clone https://github.com/Venkatreddy111/Email-formalizer.git

!cp /content/app.py  # Adjust paths as needed
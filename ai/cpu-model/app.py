from flask import Flask, render_template, request
import torch
from bigdl.llm.transformers import AutoModelForCausalLM
from transformers import LlamaTokenizer

app = Flask(__name__)

# Model prompt info
Vicuna_PROMPT_FORMAT = "### Human:\n{prompt} \n ### Assistant:\n"

# Model Path
model_path = "/root/vicuna-7b-v1.5-16k/"
model = AutoModelForCausalLM.from_pretrained(model_path, load_in_4bit=True)
tokenizer = LlamaTokenizer.from_pretrained(model_path)

def generate_response(prompt, n_predict):
    prompt = Vicuna_PROMPT_FORMAT.format(prompt=prompt)
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    
    output = model.generate(input_ids, use_cache=True, max_new_tokens=n_predict)
    output_str = tokenizer.decode(output[0], skip_special_tokens=True)
    return output_str

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    user_input = request.form['user_input']
    response = generate_response(user_input, 128)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0')

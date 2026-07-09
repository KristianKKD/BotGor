import logging
logging.getLogger("transformers.generation.utils").setLevel(logging.ERROR)

import torch
import gc
from transformers import pipeline, TextGenerationPipeline, PreTrainedTokenizer, PreTrainedModel
from transformers import AutoModelForCausalLM, AutoTokenizer

class AIBot:
    def __init__(self, model_id:str,
                 trigger:str = "?",
                 prefix:str= "A viewer says:",
                 suffix:str="Here is your reply:",
                 initial_prompt:str="",
                 enable_context:bool=False
                 ):
        
        self.model_id:str = model_id
        self.trigger:str = trigger
        self.prefix:str = prefix
        self.suffix:str = suffix
        self.context:list[str] = [initial_prompt]
        self.context_enabled:bool = enable_context

        self.busy:bool = True

        MODEL_PATH:str = "D:\AI MODELS\models"

        print(f"Loading {self.model_id}...")
        model:PreTrainedModel = AutoModelForCausalLM.from_pretrained(
            self.model_id, torch_dtype="auto", cache_dir=MODEL_PATH, device_map="cuda",
        )
        tokenizer:PreTrainedTokenizer = AutoTokenizer.from_pretrained(
            self.model_id, cache_dir=MODEL_PATH
        )

        self.text_pipe:TextGenerationPipeline = pipeline(
            task="text-generation",
            model=model,
            tokenizer=tokenizer,
            torch_dtype=torch.bfloat16,
            device_map="cuda",
            clean_up_tokenization_spaces=False
        )
        print(f"{self.model_id} loaded!")
        self.busy = False

        return

    def __del__(self):
        self.text_pipe = None
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
        gc.collect()
        return

    async def generate_response(self, prompt:str, context:str="", temperature=0.7, max_new_tokens=500, raw=False) -> str:
        self.busy = True

        if not context:
            context = '\n'.join(self.context)

        if not raw:
            prompt = f"{context}\n{self.prefix}\n{prompt}.\n{self.suffix}"

        output = self.text_pipe(prompt, temperature=temperature, max_new_tokens=max_new_tokens)

        if self.context_enabled:
            self.save_context(message=output)

        #remove the prompt from the output
        response:str = output[0]['generated_text']
        response = response.replace(prompt, "").strip()
        response = response.replace('\n', '')

        self.busy = False
        return response

    def save_context(self, message:str):
        self.context.append(message)
        return
    
    def create_prompt(self, user:str, content:str) -> str:
        return f"{user} said {content}"

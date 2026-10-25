import logging
logging.getLogger("transformers.generation.utils").setLevel(logging.ERROR)

import asyncio
import torch
from transformers import pipeline, TextGenerationPipeline, PreTrainedTokenizer, PreTrainedModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

class AIBot:
    def __init__(self, model_id:str,
                 trigger:str = "?",
                 prefix:str= "A viewer says:",
                 suffix:str="Here is your reply:",
                 initial_prompt:str="",
                 enable_context:bool=False,
                 stop_sequences:list[str] = None,
                 ):
        
        self.model_id:str = model_id
        self.trigger:str = trigger
        self.prefix:str = prefix
        self.suffix:str = suffix
        self.context:list[str] = [initial_prompt]
        self.context_enabled:bool = enable_context
        self.abort_phrases:list[str] = [self.prefix]
        if stop_sequences:
            self.abort_phrases.extend(stop_sequences)

        self.busy:bool = True

        MODEL_PATH:str = "D:\AI MODELS\models"

        print(f"Loading {self.model_id}...")
        
        quantization_config:BitsAndBytesConfig = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        model:PreTrainedModel = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            quantization_config=quantization_config,
            cache_dir=MODEL_PATH,
            device_map="cuda"
        )

        tokenizer:PreTrainedTokenizer = AutoTokenizer.from_pretrained(
            self.model_id, 
            cache_dir=MODEL_PATH,
            pad_token=None
        )
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        self.text_pipe:TextGenerationPipeline = pipeline(
            task="text-generation",
            model=model,
            tokenizer=tokenizer,
            device_map="cuda",
            clean_up_tokenization_spaces=False
        )
        
        try:
            print("Applying torch.compile optimization...")
            self.text_pipe.model = torch.compile(self.text_pipe.model, mode="reduce-overhead")
        except Exception as e:
            print(f"Warning: torch.compile failed ({e}), continuing without it")

        print(f"{self.model_id} loaded into {model.device}!")
        print("Using GPU:", torch.cuda.is_available())
        print("Model device:", next(model.parameters()).device)
        self.busy = False

        return

    def __del__(self):
        self.text_pipe = None
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
        return

    async def generate_response(self, user:str, prompt:str, context:str="", temperature=0.7, max_new_tokens=100, raw=False) -> str:
        self.busy = True
        try:
            if not context:
                context = '\n'.join(self.context)

            if not raw:
                prompt = f"{context}\n{self.prefix}\n{prompt}.\n{self.suffix}"

            # Inference
            output:list[dict[str, str]] = await asyncio.to_thread(
                self.text_pipe,
                prompt,
                temperature=temperature,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1,
                use_cache=True,
                pad_token_id=self.text_pipe.tokenizer.eos_token_id,
                eos_token_id=self.text_pipe.tokenizer.eos_token_id,
                return_full_text=False  # Only return generated text, not the prompt
            )

            # Extract the response
            response:str = output[0]['generated_text']
            if prompt in response:
                response = response.replace(prompt, "").strip()
            
            # # Stop at any of the stop sequences
            # for stop_seq in self.abort_phrases:
            #     if stop_seq and stop_seq.lower() in response.lower():
            #         response = response.split(stop_seq)[0]
            
            # # Clean up the response
            # response = response.strip()

            # # Remove markdown code blocks if present
            # if response.startswith("```"):
            #     lines = response.split('\n')
            #     response = '\n'.join(lines[1:-1]) if len(lines) > 2 else response
            #     response = response.strip()
            
            # Remove newlines for single-line response
            response = response.replace('\n', ' ').strip()

            if self.context_enabled:
                self.add_to_context(user=user, prompt=prompt, message=response)

            return response
        finally:
            self.busy = False

    def add_to_context(self, user:str, prompt:str, message:str):
        self.context.append(f"{user}:{message}")
        self.context.append(f"BotGor:{message}")
        return
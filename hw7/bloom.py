from transformers import BloomForCausalLM
from transformers import BloomTokenizerFast
import argparse
from datasets import load_dataset
import torch

def generate_text(args):
    tokenizer = BloomTokenizerFast.from_pretrained(f"bigscience/{args.model}")
    model = BloomForCausalLM.from_pretrained(f"bigscience/{args.model}")
    model.to("cuda" if torch.cuda.is_available() else "cpu")

    prompt, new_examples, answers = make_prompt(args)

    for new_example in new_examples:
        prompts = generate_prompt(prompt, new_example)
        input_ids = tokenizer(prompts, return_tensors="pt").input_ids
        input_ids = input_ids.to("cuda" if torch.cuda.is_available() else "cpu")

        if args.decoding_strategy == "top_k":
            output = model.generate(input_ids, max_new_tokens=args.max_new_tokens, do_sample=args.do_sample, \
                        top_k=args.top_k, temperature=args.temperature, num_return_sequences=args.num_return_sequences)
        elif args.decoding_strategy == "top_p":
            output = model.generate(input_ids, max_new_tokens=args.max_new_tokens, do_sample=args.do_sample, \
                        top_p=args.top_p, temperature=args.temperature, num_return_sequences=args.num_return_sequences)
        elif args.decoding_strategy == "beam_search":
            output = model.generate(input_ids, max_new_tokens=args.max_new_tokens, do_sample=args.do_sample, \
                        num_beams=args.num_beans, temperature=args.temperature, num_return_sequences=args.num_return_sequences)
        elif args.decoding_strategy == "greedy":
            output = model.generate(input_ids, max_new_tokens=args.max_new_tokens, do_sample=False, \
                        temperature=args.temperature, num_return_sequences=args.num_return_sequences)
        else:
            raise ValueError("Decoding strategy not supported")

        output_text = tokenizer.decode(output[0], skip_special_tokens=True)


        with open(args.output, "a") as f:
            f.write(f"{output_text}\n\n\n")
            f.write(f"------------------------------------------------\n\n\n")

    with open(args.output, "a") as f:
            f.writelines(f"{answers}")

def make_prompt(args):
    dataset = load_dataset("boolq")
    examples = dataset["train"].shuffle(seed=args.seed)
    prompt_yes = [f"\nQUESTION: {examples['question'][i]} \n PASSAGE: {examples['passage'][i]} \n ANSWER: {examples['answer'][i]}" for i in range(20) if examples['answer'][i] == True]
    prompt_no = [f"\nQUESTION: {examples['question'][i]} \n  PASSAGE: {examples['passage'][i]}  \n ANSWER: {examples['answer'][i]}" for i in range(20) if examples['answer'][i] == False]
    prompt = [p for pair in zip(prompt_yes, prompt_no) for p in pair]
    answers = [examples['answer'][i] for i in range(args.num_examples+100, args.num_examples+200)]
    new_examples = [f"\nQUESTION: {examples['question'][i]}  \n PASSAGE: {examples['passage'][i]}  \n ANSWER: " for i in range(args.num_examples+100, args.num_examples+200)]

    return prompt, new_examples, answers

def generate_prompt(prompt, new_example):
    prompts = " ".join(prompt + [new_example])
    return prompts


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="input.txt")
    parser.add_argument("--output", type=str, default="output.txt")
    parser.add_argument("--model", type=str, choices=["bloomz-560m",  "bloomz-1b7", "bloomz-1b7", "bloomz-3b"], default="bloomz-560m")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top_k", type=int, default=50)
    parser.add_argument("--top_p", type=float, default=0.95)
    parser.add_argument("--max_length", type=int, default=1000)
    parser.add_argument("--num_return_sequences", type=int, default=1)
    parser.add_argument("--do_sample", type=bool, default=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max_new_tokens", type=int, default=10)
    parser.add_argument("--decoding_strategy", type=str, default="top_k", choices=["top_k", "top_p", "beam_search", "greedy"])
    parser.add_argument("--num_beams", type=int, default=5)
    parser.add_argument("--num_examples", type=int, default=8)
    args = parser.parse_args()

    generate_text(args)

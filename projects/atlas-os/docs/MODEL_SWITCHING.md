# Atlas OS Model Switching Guide

How to switch Atlas between different LLM backends.

## Quick Reference

```bash
# Test current configuration
atlas-llm list

# Test a specific provider
atlas-llm test -p ollama
atlas-llm test -p openai

# Generate with specific model
atlas-llm generate "Hello" -p openai -m gpt-4o

# Run evaluation on a model
atlas-eval run -p openai -m gpt-4o-mini
```

## Supported Providers

### 1. Ollama (Local Models)

Best for: Privacy, offline use, cost savings, fine-tuned models.

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.2
ollama pull qwen2.5:7b

# Test connection
atlas-llm test -p ollama -m llama3.2
```

**Configuration:**
```json
{
  "providers": {
    "ollama": {
      "base_url": "http://localhost:11434",
      "default_model": "llama3.2",
      "embed_model": "nomic-embed-text"
    }
  }
}
```

### 2. OpenAI

Best for: High capability, reliability, no local GPU needed.

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Test connection
atlas-llm test -p openai
```

**Models:**
- `gpt-4o` — Best quality
- `gpt-4o-mini` — Fast, cheap, good
- `gpt-4-turbo` — Good balance

### 3. Together.ai

Best for: Open-source models without local GPU, good pricing.

```bash
# Set API key
export TOGETHER_API_KEY="..."

# Test connection
atlas-llm test -p together
```

**Models:**
- `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo`
- `mistralai/Mixtral-8x22B-Instruct-v0.1`
- `Qwen/Qwen2.5-72B-Instruct-Turbo`

### 4. Local vLLM Server

Best for: High-performance local inference, production deployments.

```bash
# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct \
  --port 8000

# Test connection
atlas-llm test -p local_vllm
```

## Changing the Default

Edit `~/clawd/projects/atlas-os/config/llm.json`:

```json
{
  "default_provider": "ollama",
  "default_model": "qwen2.5:7b"
}
```

Or create a fresh config:
```bash
atlas-llm config --init
```

## Switching for Fine-Tuned Atlas

When we fine-tune an Atlas model, update the config:

```json
{
  "default_provider": "ollama",
  "default_model": "atlas-v1:latest",
  "providers": {
    "ollama": {
      "base_url": "http://localhost:11434",
      "default_model": "atlas-v1:latest"
    }
  }
}
```

Then test:
```bash
atlas-llm test
atlas-eval run
```

## Evaluation Workflow

1. **Baseline current model:**
   ```bash
   atlas-eval run -p openai -m gpt-4o-mini
   ```

2. **Test new model:**
   ```bash
   atlas-eval run -p ollama -m qwen2.5:7b
   ```

3. **Compare results:**
   ```bash
   atlas-eval compare \
     data/eval/eval_gpt-4o-mini_*.json \
     data/eval/eval_qwen2.5_7b_*.json
   ```

4. **Switch if better:**
   ```bash
   # Edit config to use new model as default
   atlas-llm config --show
   ```

## Programmatic Usage

```python
from llm import create_adapter, Message, GenerateConfig

# Create adapter for specific provider
llm = create_adapter("ollama", "qwen2.5:7b")

# Or use default from config
llm = create_adapter()

# Generate
result = llm.generate([
    Message.system("You are Atlas."),
    Message.user("Hello!")
])
print(result.content)

# Stream
for chunk in llm.generate_stream(messages):
    print(chunk.content, end="")
```

## Troubleshooting

### Ollama not connecting
```bash
# Check if running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

### API key not found
```bash
# Check environment
echo $OPENAI_API_KEY
echo $TOGETHER_API_KEY

# Add to shell config
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
```

### Model not found
```bash
# List available models
atlas-llm models -p ollama
atlas-llm models -p openai
```

---

*Last updated: 2026-02-03*

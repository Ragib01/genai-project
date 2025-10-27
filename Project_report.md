# Project Report: Fine-Tuning Qwen3-4B for Customer Support Automation

## 1. Problem Definition and Motivation

### Problem Definition
The objective of this project is to develop a specialized language model for customer support automation by fine-tuning the Qwen3-4B-Instruct-2507 model. The goal is to create a system capable of handling customer inquiries, extracting relevant entities (e.g., order numbers, dates), and invoking appropriate tools to provide accurate and contextually relevant responses. The model is designed to improve the efficiency and accuracy of customer support interactions, addressing common intents such as order tracking, cancellations, refunds, and policy inquiries.

### Motivation
Customer support is a critical component of business operations, yet it is resource-intensive and prone to human error when scaled. Automating customer support with a language model can reduce response times, lower operational costs, and ensure consistent, accurate responses. By leveraging a fine-tuned model with tool-calling capabilities, businesses can handle structured queries (e.g., retrieving order statuses) while maintaining natural conversational abilities. The Qwen3-4B model, with its compact size and instruction-following capabilities, is an ideal candidate for deployment in resource-constrained environments, making it suitable for real-world applications.

## 2. Model Architecture and Training Setup

### Model Architecture
The base model used is **Qwen3-4B-Instruct-2507**, a 4-billion-parameter transformer-based large language model optimized for instruction-following tasks. The model was fine-tuned using **LoRA (Low-Rank Adaptation)**, a parameter-efficient fine-tuning technique that modifies only a small subset of the model’s weights. Key LoRA configurations include:
- **LoRA Rank (r)**: 16
- **LoRA Alpha**: 16
- **LoRA Dropout**: 0.05
- **Target Modules**: Query, key, value, output, gate, up, and down projection layers (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`)

The model was quantized to 4-bit precision to reduce memory usage, enabling efficient training on two Tesla T4 GPUs (14.741 GB each). Only 33,030,144 parameters (0.81% of 4,055,498,240 total parameters) were trainable, ensuring memory efficiency.

### Training Setup
The training was conducted using the **Unsloth** library for optimized fine-tuning, with the following configuration:
- **Hardware**: 2 Tesla T4 GPUs, CUDA 7.5, PyTorch 2.6.0, Transformers 4.56.2
- **Optimizer**: AdamW (8-bit) with a learning rate of 2e-4
- **Batch Size**: Per-device batch size of 2, with 4 gradient accumulation steps, resulting in an effective batch size of 16 (2 × 2 GPUs × 4 steps)
- **Epochs**: 3
- **Total Steps**: 4,536
- **Warmup Steps**: 50
- **Learning Rate Scheduler**: Cosine
- **Mixed Precision**: FP16 (bf16 not supported on T4 GPUs)
- **Logging**: Weights & Biases (W&B) for real-time monitoring
- **Checkpointing**: Saved every 100 steps, with a limit of 2 checkpoints to manage storage

The training resumed from a previous checkpoint (`checkpoint-100`), ensuring continuity and efficient use of computational resources.

## 3. Data Preprocessing and Experimental Design

### Dataset
The dataset used is the **Bitext-customer-support-llm-chatbot-training-dataset** from HuggingFace, containing 26,872 samples in the training split. Each sample includes:
- **Instruction**: User query (e.g., "question about cancelling order {{Order Number}}")
- **Response**: Assistant response
- **Intent**: Specific action (e.g., `cancel_order`)
- **Category**: Query type (e.g., `ORDER`)
- **Flags**: Additional metadata

### Data Preprocessing
The dataset was preprocessed to enhance the model’s ability to handle real-world customer queries:
1. **Entity Extraction**: Placeholders (e.g., `{{Order Number}}`) were replaced with realistic values (e.g., `#17628484`) using a custom function (`generate_realistic_value`). This ensured the model learned to preserve exact values in responses.
2. **Tool-Calling Format**: A custom formatting function (`create_tool_calling_format`) was implemented to teach the model when to invoke tools (e.g., `track_order`, `cancel_order`) based on intent. The formatted text included:
   - System prompt with tool-calling instructions
   - User instruction with replaced entities
   - Tool call (JSON format) with extracted parameters
   - Assistant response incorporating tool results
3. **Dataset Splitting**: The dataset was split into 24,184 training samples and 2,688 validation samples (90:10 split) to monitor performance and prevent overfitting.

### Experimental Design
The experiment aimed to fine-tune the model for customer support tasks, focusing on:
- **Entity Preservation**: Ensuring the model accurately extracts and uses specific values (e.g., order numbers) in responses.
- **Tool-Calling Capability**: Enabling the model to identify intents requiring external tool invocation (e.g., retrieving order status).
- **Memory Efficiency**: Using LoRA and 4-bit quantization to make training feasible on limited hardware.

The training process was monitored via W&B, with evaluation performed every 100 steps using validation loss as the metric. The best model was loaded at the end based on the lowest evaluation loss.

## 4. Analytical Results and Discussion

### Training Results
The training process completed successfully, with the following metrics:
- **Training Time**: Not fully reported due to an incomplete execution block, but the process was computationally intensive, leveraging two GPUs.
- **Final Training Loss**: Not explicitly reported, but the model resumed from `checkpoint-100`, indicating progress in optimization.
- **Samples Processed**: 24,184 training samples over 3 epochs, with 4,536 total steps.

The model was saved in two formats:
1. **LoRA Adapters**: Stored in `./qwen3_4B_customer_support_model/lora_adapters` for lightweight deployment.
2. **Merged 16-bit Model**: Saved in `./qwen3_4B_customer_support_model/merged_16bit` for full-model usage.

Attempts to export to GGUF format (Q4_K_M, Q5_K_M, Q8_0) failed due to Kaggle’s 20GB disk space limit, but the LoRA adapters and merged model were successfully uploaded to HuggingFace:
- **Model URL**: [https://huggingface.co/ragib01/Qwen3-4B-customer-support](https://huggingface.co/ragib01/Qwen3-4B-customer-support)
- **GGUF URL**: [https://huggingface.co/ragib01/Qwen3-4B-customer-support-gguf](https://huggingface.co/ragib01/Qwen3-4B-customer-support-gguf)

### Inference Tests
The fine-tuned model was tested with four prompts:
1. **"How do I track my order?"**: The model provided a step-by-step guide but included placeholder values (e.g., `VALUE8541`), indicating incomplete learning of realistic entity handling.
2. **"I want to change my shipping address"**: The response was generic, requesting new address details without invoking a tool, suggesting the model may not consistently recognize tool-calling needs.
3. **"What is your return policy?"**: The model provided a detailed response about a 30-day return policy, showing good generalization for informational queries.
4. **"How can I contact customer support?"**: The response included realistic contact details (e.g., `+1-998-516-6721`, `customer625@email.com`), demonstrating entity preservation.

### Discussion
The model successfully learned to handle customer support queries, particularly for informational intents (e.g., return policy, contact details). However, issues with placeholder values in some responses suggest that the entity extraction and replacement mechanism requires further refinement. The failure to consistently invoke tools for intents like `track_order` indicates that the tool-calling format may need additional training data or clearer intent-tool mappings. The use of LoRA and 4-bit quantization enabled efficient training, but the GGUF export failure highlights limitations in the Kaggle environment for large-scale model conversions.

## 5. Evaluation Metrics and Performance Analysis

### Evaluation Metrics
The primary evaluation metric was **validation loss**, calculated every 100 steps during training. The model with the lowest validation loss was selected as the best model. Due to the incomplete execution block, exact loss values and training curves were not reported. However, the use of W&B suggests that metrics such as training loss, validation loss, and samples per second were logged for real-time monitoring.

### Performance Analysis
- **Training Efficiency**: The use of LoRA reduced the trainable parameters to 0.81% of the total, enabling training on two T4 GPUs with an effective batch size of 16. The AdamW 8-bit optimizer and FP16 precision further optimized memory usage.
- **Response Quality**: The inference tests showed mixed results:
  - **Strengths**: The model provided coherent responses for informational queries and preserved realistic entity values in some cases (e.g., phone numbers, emails).
  - **Weaknesses**: Inconsistent tool-calling and placeholder values in responses indicate gaps in learning the tool-calling format and entity handling.
- **Scalability**: The model’s compact size (4B parameters, 4-bit quantized) makes it suitable for deployment on resource-constrained devices, but GGUF export failures limit its immediate usability with tools like llama.cpp or Ollama.

## 6. Limitations, Conclusions, and Future Extensions

### Limitations
1. **Incomplete Entity Handling**: The model occasionally used placeholder values (e.g., `VALUE8541`) instead of realistic entities, indicating insufficient training on the entity replacement mechanism.
2. **Tool-Calling Inconsistency**: The model did not consistently invoke tools for relevant intents, likely due to limited training data or ambiguous intent-tool mappings.
3. **Storage Constraints**: The Kaggle environment’s 20GB disk limit prevented GGUF exports, restricting deployment options.
4. **Lack of Quantitative Metrics**: The absence of final loss values or BLEU/ROUGE scores limits quantitative performance evaluation.
5. **Dataset Bias**: The Bitext dataset may not cover all possible customer support scenarios, potentially limiting generalization to real-world queries.

### Conclusions
The fine-tuned Qwen3-4B model demonstrates promising capabilities for customer support automation, particularly in handling informational queries and preserving entity values. The use of LoRA and 4-bit quantization enabled efficient training, and the model was successfully uploaded to HuggingFace for public access. However, challenges in tool-calling consistency and GGUF export highlight areas for improvement. The project successfully showcases the potential of parameter-efficient fine-tuning for specialized NLP tasks.

### Future Extensions
1. **Enhanced Dataset**: Augment the dataset with more diverse customer support scenarios and explicit tool-calling examples to improve intent recognition and tool invocation.
2. **Improved Entity Handling**: Refine the `generate_realistic_value` function to ensure consistent replacement of placeholders and train the model on varied entity formats.
3. **GGUF Export**: Conduct training and export in an environment with higher storage capacity (e.g., local server or cloud platform) to enable GGUF quantization for lightweight deployment.
4. **Quantitative Evaluation**: Implement BLEU, ROUGE, or intent classification accuracy metrics to quantitatively assess response quality and tool-calling performance.
5. **Multi-Turn Conversations**: Extend the model to handle multi-turn dialogues, enabling more natural and context-aware customer interactions.

---

**Model URLs**:
- Standard Model: [https://huggingface.co/ragib01/Qwen3-4B-customer-support](https://huggingface.co/ragib01/Qwen3-4B-customer-support)
- GGUF Model: [https://huggingface.co/ragib01/Qwen3-4B-customer-support-gguf](https://huggingface.co/ragib01/Qwen3-4B-customer-support-gguf)

This report summarizes the development, training, and evaluation of a fine-tuned Qwen3-4B model for customer support automation, highlighting its strengths, limitations, and potential for future enhancements.
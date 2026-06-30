## Fixed: CLIP Evaluation Prompt Token Overflow

- 55 words 이하로 retry prompt를 줄였더라도 CLIP tokenizer 기준으로는 79 tokens가 되어 77 token 제한을 넘을 수 있었습니다.
- word count와 CLIP token count는 다를 수 있으므로 generation prompt를 그대로 evaluation에 사용하는 것은 안전하지 않습니다.
- 수정: generation prompt와 evaluation prompt를 분리했습니다. `PromptCompressor.make_evaluation_prompt()`가 caption 핵심, user prompt 핵심, style keyword, quality keyword만 포함한 35~40 words 이하의 CLIP-safe prompt를 생성합니다.
- 현재 initial evaluation은 `evaluation_prompt`, retry evaluation은 `retry_evaluation_prompt`를 사용합니다.

## Fixed: Retry Prompt CLIP Token Overflow

- Sprint20 RAG Style Library 이후 initial prompt는 압축되었지만, retry 단계의 `suggested_prompt`가 prompt budget을 거치지 않고 generation/evaluation에 사용되는 문제가 있었습니다.
- 이로 인해 retry CLIP evaluation에서 `Sequence length must be less than max_position_embeddings (91 > 77)` 오류가 발생할 수 있었습니다.
- 수정: `PromptCompressor.compress_prompt(prompt, max_words=55)`를 추가하고, `DynamicExecutionEngine` retry 단계에서 raw suggested prompt와 compressed retry prompt를 분리했습니다.
- 현재 retry generation/evaluation은 `retry_prompt`만 사용하며, memory record에는 `raw_suggested_prompt`와 `retry_prompt`를 구분해 저장합니다.

# Known Issues

- Hugging Face token 환경변수가 없으면 FLUX는 fallback image를 사용합니다.
- 첫 BLIP/CLIP 실행 시 모델 다운로드로 시간이 오래 걸릴 수 있습니다.
- CLIP score는 prompt alignment만 주로 평가하며 이미지 품질 전체를 의미하지 않습니다.
- mock fallback image는 실제 생성 품질 평가에 한계가 있습니다.
- Windows 환경에서는 LF/CRLF warning이 발생할 수 있습니다.
- 실제 BLIP/CLIP/FLUX 동작은 network, model cache, API quota, device 환경에 영향을 받습니다.
- CLIP similarity 계산 중 model output 객체를 tensor처럼 사용하는 버그가 발견됐고, `get_image_features()`와 `get_text_features()`에서 얻은 tensor를 정규화해 cosine similarity를 계산하도록 수정했습니다.
- CLIP `BaseModelOutputWithPooling` 객체에 `.norm()` 또는 cosine similarity를 적용하던 문제를 수정했습니다. 현재는 반드시 `get_image_features()`와 `get_text_features()`가 반환한 Tensor에만 `F.normalize()`를 적용합니다.
- runtime output은 `outputs/`에 생성되지만 전체 폴더를 Git에 올리는 방식은 권장하지 않습니다. demo에 필요한 선별 이미지만 `assets/demo/`에 보관하는 방향을 사용합니다.

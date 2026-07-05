# Interview Notes

## v2.4 Real IP-Adapter Integration Questions

Q. SDXL Img2Img와 IP-Adapter의 역할 차이는 무엇인가요?
A. SDXL Img2Img는 reference image의 구조와 composition을 generation 시작점으로 사용합니다. IP-Adapter는 reference image feature를 별도로 주입해 identity, hair, outfit, visual style 보존을 강화합니다.

Q. Style Prompt는 어떤 역할인가요?
A. Style Prompt는 identity를 설명하지 않고 style, lighting, quality, mood, camera, rendering만 제어합니다. Identity는 reference image와 IP-Adapter가 담당합니다.

Q. IP-Adapter가 실패하면 workflow는 어떻게 동작하나요?
A. Crash하지 않고 SDXL Img2Img prompt/style-only 경로로 fallback합니다. Debug Report에는 `ip_adapter_enabled`, `ip_adapter_loaded`, `ip_adapter_scale`, `used_conditioning_fallback`, `conditioning_fallback_reason`이 저장됩니다.

Q. 학습 없이 어떻게 IP-Adapter를 사용하나요?
A. 이 프로젝트는 adapter를 학습하지 않습니다. 공개 또는 로컬 adapter weight를 `IP_ADAPTER_MODEL_PATH`와 `IP_ADAPTER_WEIGHT_NAME`으로 지정해 inference-only로 로드합니다.

## v2.3 SDXL Style Prompt Renderer Questions

Q. 왜 SDXL에서는 Prompt를 줄였나요?
A. SDXL Img2Img는 reference image를 직접 입력으로 받기 때문에 identity를 긴 텍스트로 다시 설명할 필요가 없습니다. 긴 prompt는 reference image와 충돌하거나 CLIP/텍스트 인코더 budget 문제를 만들 수 있으므로, SDXL에는 style 중심의 짧은 prompt를 사용합니다.

Q. 왜 Identity를 Prompt에서 제거했나요?
A. Identity, gender, hair, outfit, eye color, accessories는 reference image가 담당해야 하는 정보입니다. Prompt에 다시 넣으면 이미지가 가진 실제 시각 단서와 텍스트 설명이 충돌할 수 있습니다. 그래서 SDXL Style Prompt는 style, lighting, quality, mood, camera, rendering만 포함합니다.

Q. Img2Img의 장점은 무엇인가요?
A. Img2Img는 reference image를 latent 변환의 출발점으로 사용합니다. 따라서 prompt-only generation보다 silhouette, pose, composition, outfit 같은 reference 구조를 더 자연스럽게 유지할 수 있습니다.

Q. FLUX와 SDXL Prompt Rendering 차이는 무엇인가요?
A. FLUX는 reference image가 provider 입력으로 직접 들어가지 않으므로 dense prompt가 필요합니다. SDXL Img2Img는 reference image가 identity를 제공하므로 StyleProgram 기반 style prompt만 사용합니다.

Q. 77 token 문제는 어떻게 해결했나요?
A. SDXLPromptRenderer가 style prompt를 60 token 이하로 제한하고, 목표는 40 token 이하로 유지합니다. Debug Report에는 style prompt, word count, token count가 저장됩니다.

## v2.4 Reference-aware Style Transfer Questions

Q. 왜 Prompt만으로 Style Transfer하지 않았나요?
A. Prompt는 원하는 스타일을 설명하지만 reference image의 identity, silhouette, outfit, pose 같은 시각적 단서를 직접 고정하지 못합니다. 그래서 style은 LoRA, identity는 IP-Adapter, structure는 ControlNet으로 분리할 수 있는 generation provider 구조가 필요합니다.

Q. LoRA는 왜 학습하지 않았나요?
A. 이 프로젝트의 목표는 학습 파이프라인이 아니라 agent framework와 provider architecture입니다. LoRA는 공개 또는 로컬 `.safetensors` weight를 inference-only로 로드하는 hook만 제공합니다.

Q. Reference Conditioning 구조의 장점은 무엇인가요?
A. reference image에서 추출한 identity/style/structure 요구를 prompt와 분리해 provider에 전달할 수 있습니다. 이렇게 하면 prompt engineering과 image conditioning이 서로 다른 책임으로 관리됩니다.

Q. IP Adapter와 LoRA 역할 차이는 무엇인가요?
A. IP-Adapter는 reference image feature를 사용해 identity/style consistency를 보강합니다. LoRA는 특정 화풍이나 렌더링 스타일을 provider에 추가하는 inference weight입니다.

Q. ControlNet은 무엇을 유지합니까?
A. ControlNet은 pose, depth, edge 같은 구조 정보를 유지하는 역할입니다. 현재는 OpenPose, Depth, Canny hook placeholder만 있고 실제 ControlNet model은 아직 연결하지 않았습니다.

## v2.3 IP-Adapter Hook Questions

Q. 왜 prompt-only generation만으로 reference 보존이 어렵나요?
A. Prompt는 reference image의 특징을 설명할 뿐, feature를 generation model에 직접 주입하지 않습니다. Hair, outfit, accessory, silhouette 같은 identity cue는 텍스트만으로 흔들릴 수 있어서 IP-Adapter 같은 image conditioning hook이 필요합니다.

Q. IP-Adapter는 이 구조에서 어떤 역할을 하나요?
A. IP-Adapter는 reference image feature를 SDXL generation provider에 전달해 identity/style preservation을 강화하는 역할입니다. 현재 구조에서는 `reference_conditioning_package`를 읽은 뒤 SDXL provider 내부에서 `load_ip_adapter`와 `set_ip_adapter_scale`을 호출하는 hook으로 배치했습니다.

Q. 학습 없이 reference-aware generation을 어떻게 구성했나요?
A. 별도 학습을 하지 않고 공개 IP-Adapter 또는 기존 adapter weight를 provider layer에서 선택적으로 로드하는 구조입니다. Framework는 adapter path, weight name, conditioning strength를 config와 debug report에 기록하고, 실제 adapter 파일이 있을 때만 사용합니다.

Q. IP-Adapter가 실패하면 workflow는 어떻게 동작하나요?
A. Crash하지 않고 prompt-only fallback으로 계속 진행합니다. `used_conditioning_fallback=true`, `conditioning_reason`, `ip_adapter_status`가 Debug Report에 저장되어 실패 원인을 추적할 수 있습니다.

## v2.2 SDXL Quality Provider Questions

Q. 왜 Txt2Img가 아니라 Img2Img를 선택했나요?
A. 목표가 단순 이미지 생성이 아니라 reference-aware style transfer이기 때문입니다. Txt2Img는 reference image를 직접 입력으로 사용하지 않지만, Img2Img는 원본 이미지를 generation 초기 조건으로 사용하므로 identity, outfit, pose, composition 같은 시각적 단서를 보존하기 좋습니다.

Q. Img2Img가 Identity Preservation에 유리한 이유는 무엇인가요?
A. Prompt는 identity를 텍스트로 설명할 뿐이지만 Img2Img는 reference image 자체를 입력으로 사용합니다. 따라서 hair color, outfit, silhouette, pose 같은 요소가 latent 변환 과정에 반영되어 prompt-only 방식보다 보존 가능성이 높습니다.

Q. Strength는 무엇을 의미하나요?
A. `strength`는 reference image를 얼마나 강하게 변형할지 조절하는 값입니다. 낮을수록 원본 구조를 더 많이 유지하고, 높을수록 prompt와 style 변화가 강해집니다. 기본값은 0.55로, 보존과 변형 사이의 균형을 목표로 합니다.

Q. 왜 IP-Adapter보다 먼저 Img2Img를 구현했나요?
A. Img2Img는 Diffusers SDXL pipeline의 기본 기능으로 reference image를 실제 generation에 연결하는 가장 단순한 첫 단계입니다. 이 경로가 안정화되면 그 다음에 IP-Adapter를 추가해 identity feature conditioning을 더 정밀하게 강화할 수 있습니다.

Q. 왜 FLUX와 SDXL을 함께 사용했나요?
A. FLUX는 빠르고 현재 workflow에서 안정적인 기본 generation path입니다. SDXL은 negative prompt, img2img, ControlNet, IP-Adapter 같은 reference-aware 확장과 잘 맞는 품질 중심 provider로 설계하기 좋습니다. 그래서 FLUX는 Fast Mode로 유지하고 SDXL은 Quality Mode로 추가했습니다.

Q. Fast Mode와 Quality Mode의 차이는 무엇인가요?
A. Fast Mode는 `flux_fast`를 사용해 빠른 생성과 기존 호환성을 우선합니다. Quality Mode는 `sdxl_quality`를 사용하고 1024x1024, 30 steps, CFG 7.5, strength 0.55로 실제 SDXL Img2Img generation을 수행합니다.

Q. 왜 Provider Router를 유지했나요?
A. Provider 선택을 generation code 안에 하드코딩하면 FLUX, SDXL, future IP-Adapter/ControlNet 경로가 섞입니다. Router를 유지하면 환경변수나 planner 결정으로 provider를 바꾸면서도 Prompt Rendering, Evaluation, Debug Report는 같은 contract를 사용할 수 있습니다.

## v2.1 Reference Conditioning Interface Questions

Q. 왜 prompt-only generation만으로 reference 보존이 어려운가요?
A. Prompt는 hair color, eye color, outfit, accessories를 텍스트로 설명할 수는 있지만 reference image의 visual feature를 직접 고정하지는 못합니다. 그래서 identity나 silhouette처럼 시각적 일관성이 중요한 경우에는 IP-Adapter, ControlNet, img2img 같은 reference-conditioned generation 경로가 필요합니다.

Q. Reference Conditioning Package는 무엇인가요?
A. Reference Conditioning Package는 reference image를 generation provider가 사용할 수 있도록 구조화한 중간 표현입니다. `conditioning_type`, identity/style/structure strength, preserve flags, reference image path, notes를 포함하며 현재는 prompt-only fallback 상태를 명시합니다.

Q. IP-Adapter는 이 구조에서 어디에 붙나요?
A. Prompt Rendering과 Reference Conditioning Package가 만들어진 뒤 Generation Provider 단계에 붙습니다. 현재는 `ip_adapter_planned`로 기록만 하고, 향후 SDXL Quality Provider 내부에서 실제 IP-Adapter 입력으로 연결할 수 있습니다.

## v2.0 Generation Quality Upgrade Questions

Q. 왜 Provider Router를 만들었나요?
A. Generation Layer가 특정 모델 하나에 묶이면 FLUX, SDXL, future IP Adapter/ControlNet 같은 경로를 바꿀 때 workflow 전체가 흔들립니다. Router를 두면 Context Program과 Prompt Rendering은 유지하면서 provider 선택과 preset만 교체할 수 있습니다.

Q. 왜 FLUX만 사용하지 않았나요?
A. FLUX fast path는 빠르고 기존 workflow에 안정적입니다. 하지만 reference image의 hair color, eye color, outfit, accessories, identity preservation은 더 정밀한 generation control이 필요할 수 있습니다. 그래서 FLUX는 Fast Mode로 유지하고, SDXL Quality Mode skeleton을 추가해 품질 중심 경로를 준비했습니다.

Q. Quality Mode는 어떤 상황에서 사용합니까?
A. 사용자가 quality, identity, preserve, high fidelity, SDXL 같은 요구를 주거나 reference image 보존이 중요한 경우 Quality Mode를 선택합니다. 이 모드는 CFG, steps, resolution, scheduler 같은 preset을 명확히 기록해 재현성과 debug 가능성을 높입니다.

Q. IP Adapter는 어디에 붙을 예정입니까?
A. IP Adapter는 Generation Router 이후 SDXL Quality Provider 내부에 붙을 예정입니다. Context Program과 Reference Image Parser가 만든 identity/accessory 정보를 provider 입력으로 넘긴 뒤, IP Adapter가 reference image preservation을 담당하는 구조가 자연스럽습니다. ControlNet도 같은 provider layer의 future hook입니다.

## v1.7 Context Cache and Incremental Execution Questions

Q. 왜 Cache를 넣었나요?
A. 같은 reference image와 prompt로 반복 실험할 때 Vision, Reference Parsing, Context Program 같은 안정적인 결과를 매번 다시 계산할 필요가 없습니다. Context Cache는 이런 중간 산출물을 저장해 재실행 비용을 줄이고, debug report로 어떤 step이 skip되었는지 설명할 수 있게 합니다.

Q. Incremental Execution의 장점은 무엇인가요?
A. 변경된 부분만 다시 실행하므로 반복 실험이 빨라지고, 실패 원인을 좁히기 쉬워집니다. 예를 들어 prompt compiler 입력이 같으면 compiler를 skip하고, generation prompt와 output file이 같으면 generation도 skip할 수 있습니다.

Q. 서비스에서는 어떤 효과가 있나요?
A. 서비스 환경에서는 같은 입력을 다시 요청하거나 사용자가 일부 옵션만 바꾸는 일이 많습니다. Incremental Execution은 비용이 큰 모델 호출과 이미지 생성을 줄이고, 응답 시간과 운영 비용을 낮추는 기반이 됩니다.

## v1.6 Evaluation Layer Stabilization Questions

Q. Evaluation Layer에서 fallback을 둔 이유는?
A. CLIP, DINO 같은 metric은 모델 로드, 이미지 경로, 토큰 길이, 실행 환경에 따라 실패할 수 있습니다. 하나의 metric 실패가 전체 generation workflow를 중단하면 agent loop가 불안정해지므로, 각 metric은 disabled fallback result를 반환하고 workflow는 계속 진행합니다.

Q. weighted score는 어떻게 계산하나요?
A. Aggregator는 enabled=true인 metric만 사용합니다. 기본 weight는 CLIP 0.40, DINO 0.25, Prompt 0.20, Aesthetic 0.15입니다. disabled metric은 weight 계산에서 제외하고, 모든 weighted metric이 disabled이면 weighted_score는 0.0이며 used_fallback=true로 기록합니다.

Q. CLIP과 DINO를 함께 쓰는 이유는?
A. CLIP은 text-image semantic alignment에 강하고, DINO는 reference image와 generated image 사이의 visual consistency를 보는 데 적합합니다. 둘은 대체 관계가 아니라 보완 관계라서 prompt alignment와 identity preservation을 분리해 설명할 수 있습니다.

## v1.5 Florence Vision Parser Questions

Q. 왜 Florence를 Caption 모델로만 쓰지 않았나요?
A. Caption은 이미지 전체를 한 문장으로 요약하기 때문에 object, accessory, bbox, composition 같은 구조 정보를 잃기 쉽습니다. Florence의 `<CAPTION>`, `<DETAILED_CAPTION>`, `<OD>` task를 분리해 실행하면 Reference Image를 prompt 이전의 structured context로 다룰 수 있습니다.

Q. Vision Result를 구조화한 이유는 무엇인가요?
A. downstream agent가 특정 VLM의 출력 형식에 의존하지 않게 하기 위해서입니다. BLIP이든 Florence든 `caption`, `detailed_caption`, `objects`, `scene`, `style`, `composition`, `provider`, `latency` 같은 공통 schema로 반환하면 ReferenceImageParser와 DebugReport가 동일한 방식으로 동작합니다.

Q. Reference Parser는 왜 Caption보다 Objects를 우선합니까?
A. object detection 결과는 sword, hat, bag 같은 identity-preserving prop을 caption보다 명확하게 전달합니다. 그래서 parser는 `objects -> detailed_caption -> caption -> fallback` 순서로 읽고, object name을 accessories와 character identity context에 반영합니다.

## v1.4 DINO Identity Metric Questions

Q. 왜 CLIP 외에 DINO를 추가했나요?
A. CLIP은 text-image semantic alignment에 강하지만 reference image와 generated image가 시각적으로 같은 캐릭터를 유지하는지는 직접 평가하기 어렵습니다. DINO는 image-image feature similarity를 통해 identity consistency를 보완합니다.

Q. CLIP과 DINO의 평가 관점은 어떻게 다른가요?
A. CLIP은 prompt text와 generated image가 의미적으로 맞는지 봅니다. DINO는 reference image와 generated image의 visual feature가 얼마나 유사한지 봅니다. 그래서 CLIP은 “요청과 맞는가”, DINO는 “참조 이미지의 시각적 정체성을 유지했는가”에 가깝습니다.

Q. reference image 기반 생성에서 DINO가 왜 유용한가요?
A. reference image 기반 생성에서는 outfit, silhouette, accessory, overall visual identity가 중요합니다. DINO는 텍스트 prompt에 드러나지 않는 visual consistency를 image-image 관점으로 평가할 수 있어 Character Preservation 품질을 설명하는 데 유용합니다.

## v1.3 Evaluation Prompt Routing Questions

Q. 왜 generation prompt를 그대로 CLIP에 넣지 않았나요?
A. generation prompt는 provider가 이미지를 만들기 위해 풍부한 style, quality, layout, negative-related context를 포함할 수 있습니다. CLIP similarity는 짧은 semantic alignment 평가에 적합하므로 긴 generation prompt를 그대로 넣으면 token overflow나 평가 왜곡이 생길 수 있습니다.

Q. CLIP prompt를 따로 만든 이유는 무엇인가요?
A. CLIP은 짧은 text budget, 보통 77 token 제한을 갖습니다. 그래서 character, outfit, action, background 같은 핵심 의미만 남긴 `clip_prompt`를 사용하고 `masterpiece`, `8k`, `ultra detailed`, negative prompt 같은 평가에 불필요한 표현은 제거했습니다.

Q. metric별 prompt routing 구조의 장점은 무엇인가요?
A. metric마다 평가 목적이 다르기 때문에 같은 prompt를 쓰면 품질이 떨어집니다. CLIP은 semantic summary, Prompt Metric은 `generation_prompt + context_program`, Aesthetic Metric은 `pickscore_prompt`, VLM Judge는 긴 비교 지시문을 사용하도록 분리하면 평가 layer를 확장하기 쉽고 debug report도 명확해집니다.

## v1.2 Prompt Rendering Engine Questions

Q. 왜 Prompt를 하나만 만들지 않았나요?
A. Generation, CLIP evaluation, human preference scoring, VLM judging은 같은 문장을 필요로 하지 않습니다. Generation은 풍부한 visual prompt가 유리하지만, CLIP은 짧은 semantic summary가 더 안전합니다. 그래서 Context Program을 여러 model-facing prompt로 렌더링했습니다.

Q. CLIP Prompt는 왜 짧게 만들었나요?
A. CLIP은 token budget이 짧고 quality-only keyword에 민감할 수 있습니다. `masterpiece`, `8k`, `ultra detailed`, negative prompt 같은 표현을 제거하고 character, outfit, action, background 중심의 40 words 이하 semantic summary를 사용합니다.

Q. Prompt Rendering Engine의 장점은 무엇인가요?
A. Context Program은 하나로 유지하면서 downstream task마다 다른 prompt view를 만들 수 있습니다. 이 구조는 generation provider, CLIP, PickScore, VLM Judge가 서로 다른 prompt 요구사항을 가져도 Context Engineering 흐름을 깨지 않습니다.

## v1.1 VLM-only Stabilization Questions

Q. 이번 v1.1에서 집중한 것은 무엇인가요?
A. 유료 LLM API 연동은 보류하고 Vision Layer 안정화에 집중했습니다. `VLM_PROVIDER=blip` 또는 `VLM_PROVIDER=florence`만 바꿔도 `vision_result`, `reference_image`, `character_program`이 같은 schema로 downstream에 전달되도록 정리했습니다.

Q. OpenAI API 없이도 동작하나요?
A. 네. 현재 기본 실행은 `LLM_PROVIDER=rule` 또는 mock fallback을 사용합니다. Vision 품질 개선은 VLM provider 교체와 structured vision schema 중심으로 진행했기 때문에 OpenAI API key가 없어도 Gradio/FastAPI workflow를 실행할 수 있습니다.

Q. Florence-2가 실패하면 어떻게 되나요?
A. `VLM_PROVIDER=florence`일 때 Florence-2 로딩을 시도합니다. 모델 로딩, 환경, 입력 이미지 문제로 실패하면 BLIP fallback을 사용하고 `provider=florence`, `model=blip_fallback_for_florence`, `used_fallback=true`, `latency`를 기록합니다.

Q. ReferenceImageParser와 CharacterProgramBuilder는 어떻게 안정화했나요?
A. ReferenceImageParser는 caption을 무조건 파싱하지 않고 `characters`, `objects`, `colors`, `composition` 같은 structured fields를 먼저 사용합니다. CharacterProgramBuilder도 `reference_image`를 우선 반영하고 caption은 fallback으로만 사용합니다.

## v1.1 Vision Layer Questions

Q. BLIP를 제거하지 않고 Florence2를 추가한 이유는 무엇인가요?
A. BLIP는 가볍고 fallback으로 안정적입니다. Florence2는 더 풍부한 reference image understanding을 위해 추가했지만, 모델 로딩이나 환경 문제가 생겨도 전체 workflow가 깨지지 않도록 BLIP를 기본 provider와 fallback으로 유지했습니다.

Q. Vision Router가 필요한 이유는 무엇인가요?
A. VisionAgent가 특정 VLM에 직접 의존하면 Florence2, Qwen2.5-VL 같은 provider를 추가할 때 agent 코드를 계속 바꿔야 합니다. Vision Router는 provider 선택과 fallback을 분리하고, VisionAgent는 표준 `vision_result`만 보게 만듭니다.

Q. Standard Vision Result Schema는 무엇인가요?
A. 모든 VLM provider가 반환해야 하는 공통 구조입니다. 현재 핵심 필드는 `caption`, `detailed_caption`, `objects`, `characters`, `scene`, `style`, `colors`, `composition`, `provider`, `used_fallback`, `latency`입니다. 이 schema 덕분에 ReferenceImageParser와 downstream agent가 provider별 코드를 갖지 않아도 됩니다.

Q. ReferenceImageParser는 왜 raw caption보다 structured fields를 먼저 보나요?
A. caption은 한 문장 요약이라 identity, outfit, object, color, composition 같은 보존 단서를 잃기 쉽습니다. structured fields가 있으면 `characters -> objects -> style -> caption` 순서로 읽어 reference image 정보를 더 안정적으로 Context Program에 전달합니다.

Q. Florence2 모델이 로드되지 않으면 어떻게 동작하나요?
A. crash하지 않고 BLIP fallback을 사용합니다. 이때 `provider=florence2`, `used_fallback=true`, `model=blip_fallback_for_florence`, `latency`가 debug report에 기록됩니다.

## v1.0 RC2 Responsibility Questions

Q. 왜 Agent를 많이 만들지 않고 Layer로 설명했나요?
A. Agent는 내부 구현 단위이고, 면접이나 문서에서 중요한 것은 책임 구조입니다. Agent 이름을 모두 나열하면 프로젝트가 복잡해 보이지만, Planning, Context, Generation, Evaluation, Infrastructure로 설명하면 전체 흐름이 빠르게 이해됩니다. 그래서 RC2에서는 Agent 중심 설명을 줄이고 Responsibility 중심으로 재정리했습니다.

Q. Layer 구조의 장점은 무엇인가요?
A. Layer 구조는 각 기능이 어디에 속하는지 명확하게 보여줍니다. 새로운 기능을 추가할 때도 먼저 어떤 책임 Layer에 속하는지 결정할 수 있어 설계가 흔들리지 않습니다. 또한 README만 읽어도 5분 안에 전체 Framework를 파악할 수 있습니다.

Q. ExecutionEngine은 Layer를 어떻게 실행하나요?
A. ExecutionEngine은 기존처럼 step 단위로 Agent를 실행합니다. 다만 RC2에서는 step을 Planning, Context, Generation, Evaluation, Infrastructure Layer로 읽을 수 있도록 주석과 로그를 정리했습니다. 실행 방식은 유지하되 이해 방식을 Layer 중심으로 바꾼 것입니다.

Q. Context Engineering은 어떤 역할을 하나요?
A. Context Engineering은 사용자 의도, reference image, memory, retrieval, provider constraint를 생성 가능한 구조로 바꾸는 역할입니다. 이 프로젝트에서는 Context Program과 Prompt Compiler가 그 중심입니다. 즉 prompt 문자열을 바로 만드는 것이 아니라, 먼저 provider-independent context를 만들고 이후 provider별 prompt package로 변환합니다.

Q. Adaptive Planning은 어디에 포함됩니까?
A. RC2 구조에서는 Adaptive Planning을 Evaluation Layer 내부의 feedback process로 봅니다. Evaluation 결과를 보고 reflection, hypothesis, strategy, retry decision을 수행하기 때문입니다. 따라서 Adaptive Planning은 별도 외부 Layer가 아니라 Evaluation & Adaptive Planning 책임 안에 포함됩니다.

## v1.0 RC1 Layer-based Questions

Q. 이 프로젝트는 단순 이미지 생성 데모와 무엇이 다른가요?
A. 단순 데모는 보통 prompt를 넣고 이미지를 받는 흐름에서 끝납니다. 이 프로젝트는 Planning, Context, Generation, Evaluation, Reasoning, Memory / Observability Layer로 나누어 입력 이해부터 평가, 재계획, 기록까지 관리합니다. 그래서 결과만 보는 것이 아니라 시스템이 무엇을 이해했고 왜 그런 결정을 했는지 추적할 수 있습니다.

Q. 왜 Layer 구조로 정리했나요?
A. Agent 수가 많아지면 개별 클래스 이름만으로는 전체 구조를 이해하기 어렵습니다. Layer 구조는 각 Agent가 어떤 책임 영역에 속하는지 보여주기 위한 설명 방식입니다. 기능을 새로 만든 것이 아니라, 기존 기능을 유지하면서 유지보수와 포트폴리오 설명이 쉬운 구조로 정리했습니다.

Q. Agent가 많아졌을 때 복잡도를 어떻게 관리했나요?
A. DynamicExecutionEngine은 실행 순서를 관리하고, ToolRegistry는 step 이름과 실제 Agent 객체를 분리합니다. 문서에서는 각 Agent를 6개 Layer에 배치해 책임을 정리했습니다. 이 방식은 새로운 Agent가 추가되어도 어느 Layer에 속하는지 먼저 결정하게 만들어 구조적 복잡도를 줄입니다.

Q. Planning Layer와 Reasoning Layer의 차이는 무엇인가요?
A. Planning Layer는 생성 전에 user intent, reference image, goal, scene, character identity를 해석합니다. Reasoning Layer는 생성 후 evaluation 결과를 바탕으로 실패 원인, 전략 선택, self verification, adaptive planning을 수행합니다. 즉 Planning은 사전 계획이고 Reasoning은 결과 기반 판단과 재계획입니다.

Q. Context Program은 왜 필요한가요?
A. Prompt 문자열을 바로 만들면 provider 제약, memory, retrieval, character identity, layout 정보가 섞여 관리하기 어렵습니다. Context Program은 이런 정보를 provider-independent structured object로 정리합니다. 이후 PromptCompiler가 이 구조를 FLUX, SDXL, GPT Image 같은 provider별 prompt package로 변환할 수 있습니다.

Q. Adaptive Planning은 단순 Retry와 무엇이 다른가요?
A. Retry는 다시 생성할지 여부를 판단하는 정책에 가깝습니다. Adaptive Planning은 왜 실패했는지 분석하고, character priority, layout rule, style balance 같은 context update를 만들어 다음 생성 전략을 바꿉니다. 그래서 단순 반복이 아니라 re-planning loop에 가깝습니다.

Q. Evaluation Layer를 왜 Multi-Metric 구조로 만들었나요?
A. CLIP similarity 하나만으로는 identity preservation, prompt completeness, aesthetic quality를 충분히 설명하기 어렵습니다. Multi-Metric Evaluation은 CLIP, Identity, Prompt, Aesthetic metric을 분리하고 weighted score와 reason을 남깁니다. 이 구조는 나중에 PickScore, DINO, VLM Judge 같은 metric을 추가하기 쉽습니다.

Q. 이 프로젝트를 실제 서비스로 확장한다면 무엇을 개선하겠습니까?
A. 먼저 Docker/CI smoke test, queue-based async generation, persistent database, object storage, auth, monitoring을 추가해야 합니다. 그 다음 multi-session memory와 benchmark dashboard를 붙여 운영 중 품질 변화를 추적할 수 있게 만들겠습니다. 또한 VLM Judge나 stronger VLM을 추가해 reference image parsing과 evaluation 품질을 높일 수 있습니다.

## Key Portfolio Questions

Q. 이 프로젝트는 단순 이미지 생성 데모와 무엇이 다른가요?
A. 단순 prompt-to-image가 아니라 Vision Understanding, Context Engineering, Prompt Compiler, Provider Routing, Multi-Metric Evaluation, Reflection, Self Verification, Strategy Selection, Adaptive Planning, Memory까지 포함한 전체 AI Agent workflow입니다.

Q. Context Program은 무엇인가요?
A. Context Program은 user intent, caption, character program, goal tree, memory, retrieval, layout, style, provider constraint를 provider-independent structured object로 정리한 중간 표현입니다. Prompt 이전 단계의 의미 구조입니다.

Q. Prompt Compiler는 왜 필요한가요?
A. Context Program은 provider-independent 구조이고, FLUX/SDXL/GPT Image 같은 provider는 서로 다른 prompt 형식이 필요합니다. Prompt Compiler는 structured context를 provider-specific prompt package로 변환합니다.

Q. Adaptive Planning은 Retry와 무엇이 다른가요?
A. Retry는 다시 생성할지 결정하는 정책이고, Adaptive Planning은 왜 실패했는지 분석한 뒤 context update와 priority change를 만들어 다음 generation 전략을 바꾸는 re-planning 단계입니다.

Q. Multi-Metric Evaluation을 도입한 이유는 무엇인가요?
A. CLIP만으로는 identity preservation, prompt completeness, aesthetic quality를 설명하기 어렵습니다. Multi-Metric Evaluation은 CLIP, Identity, Prompt, Aesthetic metric을 분리하고 weighted score와 reason을 남깁니다.

Q. 실제 서비스로 확장하려면 무엇을 추가해야 하나요?
A. Docker/CI, queue-based async execution, auth, persistent database, object storage, monitoring, benchmark dashboard, multi-session memory, stronger provider error handling이 필요합니다.

## Table of Contents

- [Architecture](#architecture)
- [Agents](#agents)
- [Prompt and Context](#prompt-and-context)
- [Provider and Models](#provider-and-models)
- [Evaluation and Retry](#evaluation-and-retry)
- [Memory and Retrieval](#memory-and-retrieval)
- [Debugging and Benchmark](#debugging-and-benchmark)
- [AI Collaboration](#ai-collaboration)
- [Future Work](#future-work)

## Architecture

Q. 이 프로젝트는 무엇인가요?
A. Planning, Retrieval, Prompt Orchestration, Provider Routing, Generation, Evaluation, Reflection, Retry, Memory를 연결한 multi-agent image generation framework입니다.

Q. 왜 multi-agent 구조인가요?
A. 이미지 생성 workflow는 captioning, context retrieval, prompt assembly, provider adaptation, evaluation처럼 역할이 다릅니다. 각 역할을 Agent로 분리하면 디버깅과 설명이 쉬워집니다.

Q. OrchestratorAgent는 왜 필요한가요?
A. 여러 Agent를 직접 연결하는 진입점입니다. 실제 실행은 DynamicExecutionEngine과 ToolRegistry가 담당하지만, Orchestrator는 agent registration과 pipeline facade 역할을 합니다.

Q. DynamicExecutionEngine의 역할은 무엇인가요?
A. Planner가 만든 execution plan을 읽고 각 step을 순서대로 실행합니다.

Q. ToolRegistry는 왜 필요한가요?
A. Agent 이름과 실행 객체를 분리해 workflow가 직접 class를 의존하지 않도록 합니다.

Q. AgentState를 도입한 이유는?
A. dict key가 많아지면서 오타와 누락 위험이 커졌기 때문입니다. AgentState는 shared state의 중심 계약입니다.

## Agents

Q. VisionAgent는 무엇을 하나요?
A. 입력 이미지를 caption으로 변환합니다. BLIP integration 또는 fallback captioning을 사용합니다.

Q. ScenePlanningAgent는 왜 필요한가요?
A. user prompt를 scene, emotion, relationship, camera intent 등 시각적 계획으로 바꿉니다.

Q. LayoutAgent는 keyword generator인가요?
A. 현재는 composition planning agent입니다. layout type, frame structure, camera view, subject placement를 계획합니다.

Q. Prompt specialist agents를 여러 개로 나눈 이유는?
A. character, style, layout, pose, expression, lighting, negative prompt는 서로 다른 prompt responsibility를 가지기 때문입니다.

Q. PromptAssembler는 왜 필요한가요?
A. specialist output을 canonical prompt로 조립하는 책임을 분리하기 위해서입니다.

## Prompt and Context

Q. Context Engineering이란?
A. Agent가 사용할 task, memory, retrieval, scene, provider constraint를 구조화하는 작업입니다.

Q. Rule 기반과 LLM 기반 Reasoning 차이는?
A. Rule 기반은 빠르고 결정적이며 fallback에 적합합니다. LLM 기반 Reasoning은 semantic conflict, priority, strategy처럼 문맥 해석이 필요한 판단에 강하지만 API 실패와 JSON parsing 실패 가능성이 있으므로 항상 rule fallback을 유지합니다.

Q. 왜 Reasoner Provider Router를 만들었나요?
A. Agent가 OpenAI 같은 특정 provider를 직접 호출하면 교체와 테스트가 어려워집니다. ReasonerRouter는 `LLM_PROVIDER`에 따라 rule, openai, gemini skeleton, claude skeleton을 선택하고 같은 JSON interface로 결과를 반환합니다.

Q. LLM 실패 시 어떻게 동작하나요?
A. API key가 없거나 client import가 실패하거나 JSON parsing이 실패하면 기존 rule 결과를 그대로 fallback으로 사용합니다. Debug metadata에는 provider, fallback 여부, latency, fallback reason을 남깁니다.

Q. 왜 LLM을 Prompt 생성에 쓰지 않고 Reasoning에 먼저 사용했나요?
A. Prompt를 바로 생성하게 하면 내부 의도 해석과 provider prompt가 섞이기 쉽습니다. 먼저 semantic planning을 구조화하면 rule-based agent와 prompt compiler가 더 안정적으로 사용할 수 있습니다.

Q. Semantic Planning Layer란 무엇인가요?
A. user intent를 scene goal, composition goal, interaction goal, style goal, priority 같은 구조화된 계획으로 바꾸는 prompt 이전 단계입니다.

Q. Rule-based Agent와 LLM Agent를 왜 분리했나요?
A. LLM은 의도 해석에 강하고, rule-based agent는 안정적인 구조화와 fallback에 강합니다. 둘을 분리하면 디버깅과 교체가 쉬워집니다.

Q. Context Program이란?
A. 여러 agent output을 provider-independent structured intermediate representation으로 정리한 객체입니다.

Q. ContextProgramBuilder는 왜 만들었나요?
A. agent state와 generation prompt가 섞이지 않게 하기 위해서입니다. 먼저 context를 구조화하고, 이후 prompt로 컴파일합니다.

Q. Context Program Validator는 왜 필요한가요?
A. Context Program이 prompt assembly 전에 필요한 section을 모두 갖췄는지, 타입이 맞는지, provider와 충돌하지 않는지 확인하기 위해서입니다.

Q. Schema validation이 AI Agent Framework에서 중요한 이유는?
A. Agent가 많아질수록 state shape이 불안정해질 수 있습니다. schema validation은 generation 전에 오류를 빨리 발견하고 debug report에 남기는 안전장치입니다.

Q. Provider compatibility는 어떻게 검사하나요?
A. provider별 제약을 rule로 확인합니다. 예를 들어 FLUX는 long prompt와 negative prompt 직접 반영에 warning을 내고, SDXL은 negative section 존재를 확인합니다.

Q. Prompt Engineering과 Context Engineering 차이는?
A. Context Engineering은 정보를 구조화하는 일이고, Prompt Engineering은 그 정보를 모델 입력 문장으로 변환하는 일입니다.

Q. Canonical Prompt는 무엇인가요?
A. provider에 종속되지 않은 기본 generation prompt입니다.

Q. Provider Prompt는 무엇인가요?
A. 특정 provider가 이해하기 좋은 형태로 변환된 prompt입니다.

Q. LLMPromptCriticAgent는 왜 필요한가요?
A. rule-based critic은 중복, 누락, 길이 문제에 강하지만 semantic conflict나 provider suitability를 충분히 보지 못합니다. LLMPromptCriticAgent는 이런 의미 기반 문제를 structured report로 진단합니다.

Q. Rule-based Critic과 LLM Critic의 차이는 무엇인가요?
A. Rule-based Critic은 deterministic check이고, LLM Critic은 의도 충돌, 우선순위, scene/layout/style 적합성을 보는 reasoning layer입니다.

Q. 왜 prompt를 바로 수정하지 않고 critique report만 생성하나요?
A. Critic과 Optimizer 책임을 분리하기 위해서입니다. Critic은 문제를 진단하고, Optimizer가 수정 여부와 방법을 결정합니다.

Q. semantic conflict는 어떻게 감지하나요?
A. 현재 mock mode에서는 user prompt와 canonical prompt의 keyword 충돌을 rule로 감지합니다. 예를 들어 photobooth intent와 battle/combat tone이 같이 있으면 conflict로 기록합니다.

Q. 실제 LLM API를 붙이지 않고 mock으로 시작한 이유는?
A. API key, 비용, 네트워크, provider 실패 없이 interface와 state flow를 먼저 검증하기 위해서입니다.

Q. 왜 LLM Client를 따로 만들었나요?
A. LLMContextReasoner, LLMPromptCritic, LLMPromptOptimizer가 각자 provider 호출 방식을 갖고 있으면 중복과 결합도가 커집니다. LLMClient는 reason, critic, optimize 호출을 공통 interface로 묶습니다.

Q. Provider Registry가 필요한 이유는?
A. mock, openai, gemini, claude, ollama 같은 provider를 agent 코드와 분리해 선택하기 위해서입니다. 지금은 mock만 구현되어 있습니다.

Q. OpenAI 대신 Mock으로 먼저 구현한 이유는?
A. API key, 네트워크, 비용 없이 dependency inversion과 provider strategy 구조를 먼저 검증하기 위해서입니다.

Q. 왜 Provider를 Agent에서 직접 호출하지 않았나요?
A. Agent가 provider API를 직접 알면 교체와 테스트가 어려워집니다. Agent는 LLMClient만 보고, provider 호출 책임은 AIModelService 아래로 숨겼습니다.

Q. AIModelService를 만든 이유는?
A. reason, critic, optimize 요청을 공통 model service boundary에서 처리하고 provider registry로 위임하기 위해서입니다.

Q. Provider Registry와 AIModelService의 차이는?
A. AIModelService는 reason/critic/optimize 요청을 받는 service layer이고, Provider Registry는 provider 이름을 실제 provider 객체로 매핑하는 factory 역할입니다.

Q. 왜 Provider를 Agent에서 직접 호출하지 않았나요?
A. Agent가 OpenAI 같은 특정 provider를 직접 호출하면 교체와 테스트가 어려워집니다. Agent는 LLMClient만 호출하고, 실제 provider 호출은 AIModelService와 ProviderRegistry 뒤에 둡니다.

Q. OpenAI API key가 없으면 어떻게 되나요?
A. OpenAIProvider는 crash하지 않고 warning을 출력한 뒤 MockProvider fallback 결과를 반환합니다. API key는 로그나 문서에 노출하지 않습니다.

Q. OpenAI 응답이 JSON이 아니면 어떻게 처리하나요?
A. raw_text를 저장하고 fallback structure를 반환하며 `used_fallback=true`로 표시합니다.

Q. Evaluation Prompt는 왜 따로 있나요?
A. CLIP token budget을 넘지 않도록 generation prompt보다 짧고 평가 중심으로 설계합니다.

Q. Retry Prompt는 무엇인가요?
A. Reflection 결과를 바탕으로 재시도에 사용하는 압축된 prompt입니다.

## Provider and Models

Q. ProviderRouter는 무엇을 하나요?
A. provider capability config를 읽고 사용 가능한 provider를 선택합니다.

Q. ProviderPromptAdapter는 왜 필요한가요?
A. FLUX, GPT Image, SDXL은 prompt 제약이 다르므로 provider별 변환 레이어가 필요합니다.

Q. PromptCompiler는 왜 필요한가요?
A. Context Program은 provider-independent 구조입니다. PromptCompiler는 이 구조를 FLUX, SDXL, GPT Image가 사용할 수 있는 provider-specific prompt package로 변환합니다.

Q. PromptAssembler와 PromptCompiler의 차이는 무엇인가요?
A. PromptAssembler는 canonical prompt를 만들고, PromptCompiler는 Context Program을 provider-specific package로 컴파일합니다.

Q. Context Program과 compiled prompt package의 차이는 무엇인가요?
A. Context Program은 구조화된 의미 표현이고, compiled prompt package는 provider 입력에 가까운 positive prompt, negative prompt, prompt blocks, budget 정보를 포함합니다.

Q. ProviderPromptAdapter와 PromptCompiler를 분리한 이유는 무엇인가요?
A. Compiler는 provider별 prompt package를 만들고, Adapter는 그 package를 최종 provider input으로 정리합니다. 이 분리로 provider별 컴파일 규칙과 실행 입력 포맷을 따로 관리할 수 있습니다.

Q. 실제 모델은 무엇을 사용하나요?
A. BLIP captioning, FLUX generation, CLIP evaluation path를 사용하며 환경에 따라 fallback이 동작할 수 있습니다.

Q. 왜 fallback을 유지하나요?
A. API token, 모델 로딩, 네트워크 문제로 전체 workflow가 깨지지 않게 하기 위해서입니다.

Q. 왜 LangGraph/CrewAI 없이 만들었나요?
A. 먼저 Python class 기반으로 agent responsibility와 state flow를 직접 학습하기 위해서입니다.

## Evaluation and Retry

Q. CLIP score는 무엇을 의미하나요?
A. image-text semantic similarity에 가깝습니다. 절대적인 이미지 품질 점수는 아닙니다.

Q. ReflectionAgent는 왜 필요한가요?
A. evaluation result를 바탕으로 실패 원인과 개선 방향을 설명합니다.

Q. RetryAgent는 왜 분리했나요?
A. retry 판단 기준을 Reflection과 분리하면 threshold나 policy를 바꾸기 쉽습니다.

Q. Retry loop는 무한 반복인가요?
A. 현재는 안정성을 위해 one-step retry 구조입니다.

## Memory and Retrieval

Q. MemoryManager는 왜 Agent가 아니라 Manager인가요?
A. Memory는 판단 주체라기보다 저장, 조회, 삭제 interface를 제공하는 infrastructure component입니다.

Q. Working Memory와 Episodic Memory 차이는?
A. Working Memory는 현재 run의 context이고, Episodic Memory는 이전 run 기록입니다.

Q. RetrievalAgent는 왜 필요한가요?
A. user prompt와 caption에 맞는 style/context knowledge를 prompt 단계에 공급합니다.

Q. JSON으로 시작한 이유는?
A. 구조가 단순하고 디버깅이 쉬우며, 추후 vector DB로 옮기기 전 interface 검증에 적합하기 때문입니다.

## Debugging and Benchmark

Q. Debug Report는 왜 필요한가요?
A. 한 run에서 어떤 prompt, score, retry, agent trace가 생겼는지 추적하기 위해서입니다.

Q. Prompt Preview는 무엇인가요?
A. 사람이 빠르게 읽을 수 있는 prompt lifecycle summary입니다.

Q. Benchmark Runner는 왜 필요한가요?
A. 여러 prompt를 반복 실행해 score, retry, provider, debug path를 비교하기 위해서입니다.

Q. Benchmark Report는 무엇인가요?
A. benchmark JSON을 Markdown/HTML 요약으로 변환한 비교 리포트입니다.

## AI Collaboration

Q. Codex를 어떻게 활용했나요?
A. Workspace rule과 allowed files를 명확히 주고, sprint별로 구현/문서/검증을 분리해 pair-programming 방식으로 사용했습니다.

Q. Prompt Engineering은 어떻게 했나요?
A. Task, Architecture, Workspace, Allowed Files, Forbidden Files, Requirements, Documentation, Done Definition 순서로 작성했습니다.

Q. 본인이 한 역할은 무엇인가요?
A. architecture 방향, sprint goal, file boundary, 검증 기준을 정하고 결과를 리뷰했습니다. Codex는 구현과 문서 초안 생성을 도왔습니다.

## Vision Provider

Q. 왜 BLIP만 직접 연결하지 않고 VLM Adapter를 만들었나요?
A. BLIP는 captioning에는 충분하지만 object, character, style, relationship parsing에는 한계가 있습니다. VisionAgent가 BLIP에 직접 의존하면 Florence-2나 Qwen-VL로 교체할 때 agent 코드를 계속 바꿔야 하므로, VLMRouter와 provider interface로 분리했습니다.

Q. BLIP의 한계는 무엇인가요?
A. 짧은 caption 생성에는 강하지만 자세한 scene graph, character attributes, layout hints, reference-image understanding을 안정적으로 구조화하기는 어렵습니다.

Q. Florence/Qwen 같은 VLM으로 어떻게 확장할 수 있나요?
A. `BaseVLM.analyze()` 인터페이스만 구현하면 됩니다. provider가 달라져도 VisionAgent는 `caption`과 `vision_result`를 같은 구조로 받습니다.

Q. 왜 Standard Vision Result Schema가 필요한가요?
A. BLIP, Florence-2, Qwen-VL이 서로 다른 출력을 내면 Reference Image Parser와 Character Program이 provider마다 다른 코드를 가져야 합니다. 표준 schema를 두면 caption, character_hints, composition_hints, color_hints를 같은 방식으로 읽을 수 있습니다.

Q. Florence/Qwen은 현재 실제로 연결되어 있나요?
A. 현재는 skeleton adapter입니다. `VLM_PROVIDER=florence` 또는 `VLM_PROVIDER=qwen`을 선택해도 기본 실행 안정성을 위해 BLIP fallback을 사용하고, `used_fallback=true`와 fallback model 이름을 vision_result에 기록합니다.

Q. BLIP fallback을 유지한 이유는 무엇인가요?
A. 무거운 VLM을 필수로 로드하면 로컬 실행성과 데모 안정성이 떨어집니다. 먼저 adapter contract와 schema를 고정하고, 실제 Florence/Qwen 연결은 같은 interface 뒤에 붙일 수 있게 준비했습니다.

Q. vision_result와 caption의 차이는 무엇인가요?
A. caption은 downstream 호환을 위한 짧은 문자열이고, vision_result는 detailed_description, objects, character_hints, style_hints, composition_hints, color_hints, model, provider, fallback 여부를 담는 구조화된 vision context입니다.

## Character Program

Q. 왜 Caption만 사용하지 않았나요?
A. Caption은 이미지 전체를 한 문장으로 요약하기 때문에 identity, outfit, accessories, color, camera composition 같은 보존 단서를 잃기 쉽습니다. Reference Image Parser는 caption을 구조화된 visual context로 바꾸어 Character Program이 더 안정적으로 캐릭터 정보를 사용할 수 있게 합니다.

Q. Reference Image Parser는 어떤 역할을 하나요?
A. VisionAgent가 만든 caption과 vision_result를 읽어 identity, appearance, style, composition, colors, identity rules를 추출합니다. 현재는 rule-based parsing이지만, 향후 Florence/Qwen 같은 VLM 결과를 더 정교하게 받아들일 수 있는 interface 역할을 합니다.

Q. Reference Image Parser와 Character Program의 관계는?
A. Reference Image Parser는 원본 이미지에서 구조적 단서를 뽑는 단계이고, Character Program은 그 단서를 generation context에서 사용할 수 있는 캐릭터 중심 표현으로 정리하는 단계입니다.

Q. Caption과 Character Program의 차이는?
A. Caption은 이미지 내용을 한 문장으로 요약한 텍스트입니다. Character Program은 gender, outfit, accessories, pose, expression, identity rules처럼 캐릭터 보존에 필요한 정보를 구조화한 데이터입니다.

Q. 왜 Character Program을 만들었나요?
A. Style Transfer와 Character Preservation에서는 단순 caption보다 캐릭터 정체성 단서가 중요합니다. Character Program은 Vision Result를 Context Program과 Prompt Compiler가 재사용할 수 있는 구조로 바꿉니다.

Q. Character Program은 Prompt와 어떻게 다른가요?
A. Prompt는 모델 입력 문장이고, Character Program은 prompt 이전 단계의 structured context입니다. Prompt Compiler가 provider별 prompt를 만들 때 필요한 identity 정보를 제공하는 중간 표현입니다.

## Goal-oriented Planning

Q. Goal Tree가 필요한 이유는?
A. Execution plan은 어떤 agent를 실행할지 정하지만, Goal Tree는 무엇을 가장 중요하게 유지할지 정합니다. 예를 들어 anime portrait에서는 identity와 face clarity가 높은 priority가 됩니다.

Q. Prompt보다 Goal을 먼저 만드는 이유는?
A. Prompt를 바로 만들면 style, identity, composition 같은 우선순위가 섞일 수 있습니다. Goal을 먼저 만들면 prompt compiler가 어떤 정보를 더 강하게 반영해야 하는지 알 수 있습니다.

Q. Goal Planning과 Adaptive Planning 차이는?
A. Goal Planning은 생성 전 목표와 priority를 세우는 사전 계획입니다. Adaptive Planning은 평가와 reflection 이후 실패 원인을 보고 다음 시도를 다시 계획하는 loop입니다.

## Adaptive Planning

Q. Retry와 Adaptive Planning의 차이는?
A. Retry는 score threshold를 기준으로 다시 생성할지 결정하는 정책입니다. Adaptive Planning은 그 전에 왜 실패했는지 분석하고, 다음 생성에서 무엇을 바꿀지 전략과 context update를 만드는 re-planning 단계입니다.

Q. 왜 Reflection만으로 끝내지 않았나요?
A. Reflection은 실패 원인을 설명하지만 실행 가능한 planning update로 변환하지는 않습니다. AdaptivePlanner는 reflection을 바탕으로 character priority, layout, style weight, camera framing 같은 변경 사항을 state에 반영합니다.

Q. Adaptive Planning은 무엇을 수정하나요?
A. 현재는 rule 기반으로 context_program의 character preservation rules, layout composition rules, style rendering rules, quality keywords를 보강하고 priority_change를 기록합니다. retry가 필요하면 prompt compiler와 provider adapter가 이 업데이트를 반영합니다.

## Strategy Selection

Q. 왜 CLIP 하나만 쓰지 않았나요?
A. CLIP은 image-text alignment에는 유용하지만 identity preservation, prompt completeness, aesthetic prompt quality를 모두 설명하지는 못합니다. Multi-Metric Evaluation은 여러 관점을 분리해 더 설명 가능한 평가를 만듭니다.

Q. Metric Aggregator를 만든 이유는?
A. 평가 기준을 metric 단위로 분리하면 PickScore, DINO, Aesthetic Score, VLM Judge 같은 새 metric을 쉽게 추가할 수 있습니다. Aggregator는 각 metric을 실행하고 weight 기반 score를 계산합니다.

Q. Metric을 추가하려면 어떻게 하나요?
A. `BaseMetric` 인터페이스를 구현하고 `evaluate(state)`가 `{name, score, reason}`을 반환하게 만든 뒤 `EvaluationAggregator`의 metric list와 weight에 추가하면 됩니다.

Q. Evaluation과 Self Verification의 차이는 무엇인가요?
A. Evaluation은 생성 이미지와 텍스트의 유사도 같은 점수를 계산합니다. Self Verification은 그 점수와 Goal Tree, Context Program, Prompt Report를 함께 보고 목표 충족 여부와 재계획 필요성을 판단합니다.

Q. 왜 Adaptive Planning 전에 Self Verification을 수행하나요?
A. Adaptive Planning은 전략을 바꾸는 단계이므로, 그 전에 현재 결과가 실제로 목표를 만족하지 못했는지 확인해야 합니다. 이렇게 하면 불필요한 retry와 prompt drift를 줄일 수 있습니다.

Q. needs_replanning은 어떻게 판단하나요?
A. best_score가 낮거나, context validation score가 낮거나, prompt missing section 또는 semantic conflict가 있거나, identity priority가 높은데 provider prompt에 preservation language가 부족하면 true가 됩니다.

Q. Self Verification은 Strategy Selector에 어떤 영향을 주나요?
A. needs_replanning이 false이면 StrategySelector가 low-risk strategy를 선택하고, blocking issue가 있으면 해당 issue를 해결하는 전략의 score를 올립니다.

Q. Strategy Selector를 만든 이유는?
A. AdaptivePlanner가 하나의 전략만 만들면 대안 비교가 어렵습니다. StrategySelector는 여러 candidate strategy를 만들고 score로 선택해 의사결정 과정을 설명 가능하게 만듭니다.

Q. Hypothesis와 Strategy의 차이는?
A. Hypothesis는 실패 원인에 대한 가설입니다. Strategy는 그 가설을 바탕으로 다음 generation에서 실제로 바꿀 행동 계획입니다.

Q. Adaptive Planning은 Strategy를 어떻게 활용하나요?
A. AdaptivePlanner는 selected_strategy를 읽어 context_updates와 priority_change를 만들고, ExecutionEngine은 이를 Context Program에 반영한 뒤 prompt compiler를 다시 실행합니다.

## Future Work

- Context Program v2 schema validation
- Docker/FastAPI deployment
- Queue-based generation
- Dashboard and benchmark dashboard
- Multi-session memory

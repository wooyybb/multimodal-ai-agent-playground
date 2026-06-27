# Sprint 9: Gradio UI Integration

## Problem

Agent workflow가 내부 코드로만 존재하여 사용자가 직접 실행하고 확인하기 어려웠습니다.

## Decision

Gradio UI를 연결하여 이미지 입력, user prompt 입력, Agent trace, score, retry 결과를 시각화합니다.

## Alternatives

- CLI only
- Streamlit
- FastAPI
- Gradio

## Reason

Gradio는 이미지 입력과 생성 결과 확인에 적합하고 MVP demo 구현이 빠릅니다. 또한 Blocks API를 사용하면 multi-output workflow를 간단하게 구성할 수 있습니다.

## Future Work

실제 BLIP/FLUX/CLIP 연결 후 demo video와 README 업데이트를 진행합니다.

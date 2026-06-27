# Known Issues

- `HF_TOKEN`이 없으면 FLUX는 fallback image를 사용합니다.
- 첫 BLIP/CLIP 실행 시 모델 다운로드로 시간이 오래 걸릴 수 있습니다.
- CLIP score는 prompt alignment만 주로 평가하며 이미지 품질 전체를 의미하지 않습니다.
- mock fallback image는 실제 생성 품질 평가에 한계가 있습니다.
- Windows 환경에서는 LF/CRLF warning이 발생할 수 있습니다.
- 실제 BLIP/CLIP/FLUX 동작은 network, model cache, API quota, device 환경에 영향을 받습니다.

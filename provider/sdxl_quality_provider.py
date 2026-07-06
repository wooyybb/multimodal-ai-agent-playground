import os
import traceback
from pathlib import Path
from time import perf_counter

from PIL import Image, ImageDraw

from generation.generation_result import GenerationResult
from generation.reference_preprocessor import ReferencePreprocessor
from provider.controlnet_hook import ControlNetHook


class SDXLQualityProvider:
    name = "sdxl_quality"
    DEFAULT_MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"

    def __init__(self, model_id: str | None = None):
        self.model_id = model_id or os.getenv("SDXL_MODEL_ID") or self.DEFAULT_MODEL_ID
        self.pipeline = None
        self.device = "cpu"
        self.torch_dtype_name = "float32"
        self.reference_preprocessor = ReferencePreprocessor()
        self.controlnet_hook = ControlNetHook()

    def generate(
        self,
        prompt: str,
        state: dict,
        fallback_generate=None,
        negative_prompt: str = "",
        config=None,
    ) -> GenerationResult:
        return self.run(prompt, negative_prompt, config, state=state)

    def run(
        self,
        prompt: str,
        negative_prompt: str = "",
        config=None,
        state: dict | None = None,
    ) -> GenerationResult:
        print("[GenerationRouter] Provider: sdxl_quality")
        print("[SDXL] Generating...")
        started = perf_counter()
        state = state or {}
        config_dict = self._config_dict(config)
        model_id = os.getenv("SDXL_MODEL_ID") or self.model_id
        self.model_id = model_id
        fallback_reason = ""
        error_type = ""
        error_repr = ""
        error_traceback = ""
        error_stage = ""
        output_path = ""
        used_fallback = False
        generation_is_mock = False
        ip_adapter_status = self._ip_adapter_status(state, config)
        reference_analysis = {}
        conditioning_summary = {}
        conditioned_reference_path = ""
        conditioning_package = {}
        controlnet_status = self.controlnet_hook.prepare(None)
        notes = [
            "real SDXL Img2Img backend",
            "StableDiffusionXLImg2ImgPipeline",
            "IP-Adapter is optional and inference-only",
            "ControlNet is optional; LoRA is not active in this sprint",
        ]

        try:
            error_stage = "reference_image"
            reference_image = self._load_reference_image(state, config)
            reference_image, conditioning_result = self._condition_reference_image(
                reference_image,
                config,
            )
            reference_analysis = conditioning_result.get("reference_analysis", {})
            conditioning_summary = conditioning_result.get("conditioning_summary", {})
            conditioned_reference_path = conditioning_result.get(
                "conditioned_reference_path",
                "",
            )
            conditioning_package = conditioning_result.get("conditioning_package", {})
            state["reference_analysis"] = reference_analysis
            state["conditioning_summary"] = conditioning_summary
            state["conditioned_reference_path"] = conditioned_reference_path
            state["conditioning_package"] = conditioning_package
            self._update_reference_conditioning_package(
                state,
                conditioned_reference_path,
                conditioning_summary,
            )
            controlnet_status = self.controlnet_hook.prepare(reference_image)
            state["controlnet_status"] = controlnet_status
            state["controlnet_enabled"] = bool(controlnet_status.get("enabled"))
            state["controlnet_loaded"] = bool(controlnet_status.get("loaded"))
            state["controlnet_type"] = controlnet_status.get("type")
            state["controlnet_scale"] = controlnet_status.get("scale")
            state["control_image_path"] = controlnet_status.get("control_image_path")
            state["controlnet_fallback_reason"] = controlnet_status.get(
                "fallback_reason",
                "",
            )
            error_stage = "pipeline_loading"
            controlnet_status = self._load_pipeline(controlnet_status)
            state["controlnet_status"] = controlnet_status
            ip_adapter_status = self._prepare_ip_adapter(reference_image, state, config)
            if ip_adapter_status.get("fallback_reason"):
                notes.append(ip_adapter_status["fallback_reason"])
                fallback_reason = ip_adapter_status["fallback_reason"]
            error_stage = "generation"
            output_path = self._run_img2img_pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                reference_image=reference_image,
                config=config,
                ip_adapter_status=ip_adapter_status,
                controlnet_status=controlnet_status,
            )
            print("[SDXL] Generation Finished")
        except Exception as error:
            used_fallback = True
            error_type = type(error).__name__
            error_repr = repr(error)
            error_traceback = traceback.format_exc()
            message = str(error) or error_repr
            fallback_reason = f"SDXL Img2Img {error_stage} failed: {message}"
            notes.append(fallback_reason)
            print(f"[SDXL] Error type: {error_type}")
            print(f"[SDXL] Error repr: {error_repr}")
            print(f"[SDXL] Error traceback:\n{error_traceback}")
            if self._mock_generation_allowed():
                generation_is_mock = True
                output_path = self._create_mock_image(prompt, config, error_stage, fallback_reason)
                mock_note = "Generated test-only mock image because ALLOW_MOCK_GENERATION=true."
                notes.append(mock_note)
                print(f"[SDXL] {mock_note}")
            else:
                print("[SDXL] No mock image generated.")

        latency = round(perf_counter() - started, 4)
        print(f"[SDXL] Latency: {latency}s")
        print(f"[SDXL] Resolution: {config_dict.get('resolution')}")
        print(f"[SDXL] Strength: {config_dict.get('strength')}")
        print(f"[SDXL] CFG: {config_dict.get('cfg')}")
        print(f"[SDXL] Steps: {config_dict.get('steps')}")
        print(f"[SDXL] Device: {self.device.upper()}")
        print(f"[SDXL] Dtype: {self.torch_dtype_name}")

        return GenerationResult(
            output_image_path=output_path,
            generation_provider=self.name,
            generation_backend="diffusers StableDiffusionXLImg2ImgPipeline",
            generation_mode="quality",
            generation_config={
                **config_dict,
                "model_id": self.model_id,
                "backend": "StableDiffusionXLImg2ImgPipeline",
                "device": self.device,
                "dtype": self.torch_dtype_name,
                "ip_adapter": ip_adapter_status,
                "controlnet": controlnet_status,
                "generation_preset": state.get("generation_preset") or {},
                "reference_analysis": reference_analysis,
                "conditioning_summary": conditioning_summary,
                "conditioned_reference_path": conditioned_reference_path,
            },
            latency=latency,
            prompt_length=len(str(prompt or "").split()),
            generation_notes=notes,
            used_fallback=used_fallback,
            generation_is_mock=generation_is_mock,
            fallback_reason=fallback_reason,
            generation_error_type=error_type,
            generation_error_repr=error_repr,
            generation_error_traceback=error_traceback,
            generation_error_stage=error_stage if used_fallback else "",
            model_id=self.model_id,
            strength=config_dict.get("strength", 0.55),
            device=self.device,
            dtype=self.torch_dtype_name,
            reference_conditioning_enabled=bool(
                (state.get("reference_conditioning_package") or {}).get("enabled")
            ),
            conditioning_type=(
                state.get("reference_conditioning_package") or {}
            ).get("conditioning_type", "img2img"),
            ip_adapter_enabled=bool(ip_adapter_status.get("enabled")),
            ip_adapter_loaded=bool(ip_adapter_status.get("loaded")),
            ip_adapter_repo_id=ip_adapter_status.get("repo_id", ""),
            ip_adapter_subfolder=ip_adapter_status.get("subfolder", ""),
            ip_adapter_weight_name=ip_adapter_status.get("weight_name", ""),
            ip_adapter_scale=float(ip_adapter_status.get("scale") or 0.75),
            used_conditioning_fallback=bool(ip_adapter_status.get("used_fallback")),
            conditioning_fallback_reason=ip_adapter_status.get("fallback_reason", ""),
            conditioning_reason=ip_adapter_status.get("reason", ""),
            ip_adapter_status=ip_adapter_status,
            style_program=state.get("style_program") or {},
            selected_lora="",
            lora_status={
                "enabled": False,
                "reason": "LoRA not implemented in this Img2Img sprint",
            },
            controlnet_status={
                **controlnet_status,
            },
            reference_analysis=reference_analysis,
            conditioning_summary=conditioning_summary,
            conditioned_reference_path=conditioned_reference_path,
            conditioning_package=conditioning_package,
        )

    def _run_img2img_pipeline(
        self,
        prompt,
        negative_prompt,
        reference_image,
        config,
        ip_adapter_status=None,
        controlnet_status=None,
    ):
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "output_sdxl_img2img.png"
        print("[SDXL] Generating with StableDiffusionXLImg2ImgPipeline...")
        kwargs = {
            "prompt": str(prompt or ""),
            "negative_prompt": negative_prompt or None,
            "image": reference_image,
            "strength": self._strength(config),
            "num_inference_steps": self._steps(config),
            "guidance_scale": self._cfg(config),
        }
        if (ip_adapter_status or {}).get("loaded"):
            kwargs["ip_adapter_image"] = reference_image
        if (controlnet_status or {}).get("loaded"):
            kwargs["control_image"] = self._load_control_image(controlnet_status)
            kwargs["controlnet_conditioning_scale"] = float(
                controlnet_status.get("scale") or 0.6
            )
        result = self.pipeline(**kwargs)
        result.images[0].save(output_path)
        return str(output_path)

    def _load_pipeline(self, controlnet_status=None):
        if self.pipeline is not None:
            print(f"[SDXL] Device: {self.device.upper()}")
            print(f"[SDXL] Dtype: {self.torch_dtype_name}")
            if (controlnet_status or {}).get("enabled") and not (
                controlnet_status or {}
            ).get("loaded"):
                return self.controlnet_hook.mark_fallback(
                    controlnet_status,
                    "ControlNet fallback: base SDXL pipeline is already loaded",
                )
            return controlnet_status or {}
        print("[SDXL] Loading Model...")
        import torch

        cuda_available = torch.cuda.is_available()
        self.device = "cuda" if cuda_available else "cpu"
        dtype = torch.float16 if cuda_available else torch.float32
        self.torch_dtype_name = "float16" if cuda_available else "float32"
        print(f"[SDXL] Device: {self.device.upper()}")
        print(f"[SDXL] Dtype: {self.torch_dtype_name}")
        controlnet_status = controlnet_status or {}
        if controlnet_status.get("enabled") and controlnet_status.get("control_image_path"):
            try:
                from diffusers import (
                    ControlNetModel,
                    StableDiffusionXLControlNetImg2ImgPipeline,
                )

                model_id = controlnet_status.get("model_id")
                if not model_id:
                    raise ValueError("CONTROLNET_MODEL_ID is not set")
                controlnet = ControlNetModel.from_pretrained(
                    model_id,
                    torch_dtype=dtype,
                    use_safetensors=True,
                )
                self.pipeline = StableDiffusionXLControlNetImg2ImgPipeline.from_pretrained(
                    self.model_id,
                    controlnet=controlnet,
                    torch_dtype=dtype,
                    use_safetensors=True,
                )
                self.pipeline = self.pipeline.to(self.device)
                return self.controlnet_hook.mark_loaded(controlnet_status)
            except Exception as error:
                reason = f"ControlNet pipeline fallback: {error or repr(error)}"
                controlnet_status = self.controlnet_hook.mark_fallback(
                    controlnet_status,
                    reason,
                )

        from diffusers import StableDiffusionXLImg2ImgPipeline

        self.pipeline = StableDiffusionXLImg2ImgPipeline.from_pretrained(
            self.model_id,
            torch_dtype=dtype,
            use_safetensors=True,
        )
        self.pipeline = self.pipeline.to(self.device)
        return controlnet_status

    def _ip_adapter_status(self, state=None, config=None):
        enabled = str(os.getenv("USE_IP_ADAPTER") or "false").lower() in {
            "1",
            "true",
            "yes",
        }
        scale = self._ip_adapter_scale(state, config)
        status = {
            "enabled": enabled,
            "loaded": False,
            "requested": enabled,
            "repo_id": os.getenv("IP_ADAPTER_REPO_ID", "h94/IP-Adapter"),
            "subfolder": os.getenv("IP_ADAPTER_SUBFOLDER", "sdxl_models"),
            "weight_name": os.getenv("IP_ADAPTER_WEIGHT_NAME", "ip-adapter_sdxl.bin"),
            "scale": scale,
            "used_fallback": False,
            "fallback_reason": "",
            "reason": "IP-Adapter pending load" if enabled else "IP-Adapter disabled",
        }
        self._log_ip_adapter_status(status)
        return status

    def _prepare_ip_adapter(self, reference_image, state=None, config=None):
        status = self._ip_adapter_status(state, config)
        if not status["enabled"]:
            return status
        if reference_image is None:
            status["used_fallback"] = True
            status["fallback_reason"] = "IP-Adapter fallback: reference image is not available"
            status["reason"] = status["fallback_reason"]
            self._log_ip_adapter_status(status)
            return status
        if not status["repo_id"]:
            status["used_fallback"] = True
            status["fallback_reason"] = "IP-Adapter fallback: IP_ADAPTER_REPO_ID is not set"
            status["reason"] = status["fallback_reason"]
            self._log_ip_adapter_status(status)
            return status
        try:
            self.pipeline.load_ip_adapter(
                status["repo_id"],
                subfolder=status["subfolder"] or None,
                weight_name=status["weight_name"] or None,
            )
            if hasattr(self.pipeline, "set_ip_adapter_scale"):
                self.pipeline.set_ip_adapter_scale(status["scale"])
            status["loaded"] = True
            status["reason"] = "IP-Adapter loaded"
        except Exception as error:
            status["loaded"] = False
            status["used_fallback"] = True
            message = str(error) or repr(error)
            status["fallback_reason"] = f"IP-Adapter fallback: {message}"
            status["reason"] = status["fallback_reason"]
        self._log_ip_adapter_status(status)
        return status

    def _log_ip_adapter_status(self, status):
        print(f"[IPAdapter] Enabled: {status.get('enabled')}")
        print(f"[IPAdapter] Repo: {status.get('repo_id', '')}")
        print(f"[IPAdapter] Subfolder: {status.get('subfolder', '')}")
        print(f"[IPAdapter] Weight: {status.get('weight_name', '')}")
        print(f"[IPAdapter] Loaded: {status.get('loaded')}")
        print(f"[IPAdapter] Scale: {status.get('scale')}")
        print(f"[IPAdapter] Fallback: {status.get('used_fallback')}")
        print(f"[IPAdapter] Reason: {status.get('fallback_reason') or status.get('reason', '')}")

    def _ip_adapter_scale(self, state=None, config=None):
        preset = (state or {}).get("generation_preset") or {}
        preset_value = preset.get("ip_adapter_scale")
        try:
            return float(os.getenv("IP_ADAPTER_SCALE") or preset_value or 0.75)
        except (TypeError, ValueError):
            return 0.75

    def _mock_generation_allowed(self):
        return str(os.getenv("ALLOW_MOCK_GENERATION") or "false").lower() in {
            "1",
            "true",
            "yes",
        }

    def _create_mock_image(self, prompt, config, error_stage, fallback_reason):
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "output_sdxl_img2img_mock.png"
        image = Image.new(
            "RGB",
            (self._width(config), self._height(config)),
            color=(238, 240, 244),
        )
        draw = ImageDraw.Draw(image)
        lines = [
            "SDXL Img2Img Mock",
            "TEST ONLY",
            f"stage: {error_stage}",
            f"steps: {self._steps(config)}",
            f"cfg: {self._cfg(config)}",
            f"strength: {self._strength(config)}",
            str(prompt or "")[:90],
            str(fallback_reason or "")[:90],
        ]
        y = 32
        for line in lines:
            draw.text((32, y), line, fill=(24, 31, 42))
            y += 32
        image.save(output_path)
        return str(output_path)

    def _load_reference_image(self, state, config):
        image_source = self._reference_image_source(state)
        if image_source is None:
            raise ValueError("reference_image is required for SDXL Img2Img generation")
        if isinstance(image_source, Image.Image):
            image = image_source.convert("RGB")
        else:
            image_path = Path(str(image_source))
            if not image_path.exists():
                raise FileNotFoundError(f"reference image not found: {image_path}")
            image = Image.open(image_path).convert("RGB")
        return image

    def _load_control_image(self, controlnet_status):
        path = controlnet_status.get("control_image_path")
        if not path:
            raise ValueError("control image path is unavailable")
        return Image.open(path).convert("RGB")

    def _condition_reference_image(self, image, config):
        return self.reference_preprocessor.condition(
            image,
            self._width(config),
            self._height(config),
        )

    def _update_reference_conditioning_package(
        self,
        state,
        conditioned_reference_path,
        conditioning_summary,
    ):
        package = dict(state.get("reference_conditioning_package") or {})
        package["conditioned_reference_path"] = conditioned_reference_path
        package["conditioning_info"] = conditioning_summary
        package["conditioned_reference"] = conditioned_reference_path
        state["reference_conditioning_package"] = package

    def _reference_image_source(self, state):
        conditioning = state.get("reference_conditioning_package") or {}
        candidates = [
            conditioning.get("reference_image_path"),
            state.get("reference_image_path"),
            state.get("image_path"),
            state.get("image"),
        ]
        for candidate in candidates:
            if candidate:
                return candidate
        return None

    def _config_dict(self, config):
        if config is None:
            return {
                "width": 1024,
                "height": 1024,
                "steps": 30,
                "cfg": 7.5,
                "strength": 0.55,
                "resolution": "1024x1024",
            }
        data = config.to_dict()
        data["strength"] = self._strength(config)
        data["resolution"] = f"{self._width(config)}x{self._height(config)}"
        data["generation_preset"] = getattr(config, "generation_preset", None) or {}
        return data

    def _width(self, config):
        return int(getattr(config, "width", 1024) or 1024)

    def _height(self, config):
        return int(getattr(config, "height", 1024) or 1024)

    def _steps(self, config):
        return int(getattr(config, "steps", 30) or 30)

    def _cfg(self, config):
        value = getattr(config, "cfg", 7.5)
        return 7.5 if value is None else float(value)

    def _strength(self, config):
        value = getattr(config, "strength", 0.55)
        return 0.55 if value is None else float(value)

from tools.flux_tool import FluxTool


class GenerationAgent:
    def __init__(self, flux_tool=None):
        self.flux_tool = flux_tool or FluxTool()

    def run(
        self,
        final_prompt: str,
        reference_conditioning_package: dict | None = None,
        provider_supports_conditioning: bool = False,
        ip_adapter_status: dict | None = None,
    ) -> str:
        print("[GenerationAgent] Running...")
        self._log_conditioning(
            reference_conditioning_package,
            provider_supports_conditioning,
            ip_adapter_status,
        )
        output_image_path = self.flux_tool.generate(final_prompt)
        print(f"[GenerationAgent] Output saved: {output_image_path}")
        return output_image_path

    def _log_conditioning(self, package, provider_supports_conditioning, ip_adapter_status=None):
        package = package or {}
        ip_adapter_status = ip_adapter_status or {}
        enabled = bool(package.get("enabled"))
        conditioning_type = package.get("conditioning_type", "none")
        print(f"[GenerationAgent] Conditioning enabled: {enabled}")
        print(f"[GenerationAgent] Conditioning type: {conditioning_type}")
        print(f"[GenerationAgent] IP-Adapter enabled: {bool(ip_adapter_status.get('enabled'))}")
        if ip_adapter_status.get("reason"):
            print(f"[GenerationAgent] Conditioning reason: {ip_adapter_status.get('reason')}")
        print(
            "[GenerationAgent] Provider supports conditioning: "
            f"{bool(provider_supports_conditioning)}"
        )

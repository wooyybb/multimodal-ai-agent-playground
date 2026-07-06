class SemanticMerge:
    GROUPS = (
        (("anime", "anime style", "anime illustration"), "anime illustration"),
        (("woman", "female", "girl", "human face"), "female character"),
        (("balanced", "balanced layout", "balanced composition"), "balanced composition"),
        (("webtoon", "webtoon style", "korean webtoon"), "soft Korean webtoon"),
        (("cinematic light", "cinematic lighting"), "cinematic lighting"),
    )

    def merge_program(self, program: dict) -> tuple[dict, dict]:
        program = self._copy_program(program)
        report = {
            "semantic_merges": [],
            "duplicates_removed": [],
        }
        for section, value in list(program.items()):
            if isinstance(value, list):
                merged, section_report = self.merge_list(value)
                program[section] = merged
                for item in section_report["semantic_merges"]:
                    report["semantic_merges"].append({"section": section, **item})
                for item in section_report["duplicates_removed"]:
                    report["duplicates_removed"].append({"section": section, "value": item})
            elif isinstance(value, dict):
                for key, nested in list(value.items()):
                    if isinstance(nested, list):
                        merged, section_report = self.merge_list(nested)
                        program[section][key] = merged
                        path = f"{section}.{key}"
                        for item in section_report["semantic_merges"]:
                            report["semantic_merges"].append({"section": path, **item})
                        for item in section_report["duplicates_removed"]:
                            report["duplicates_removed"].append(
                                {"section": path, "value": item}
                            )
        return program, report

    def merge_list(self, values) -> tuple[list, dict]:
        result = []
        seen = set()
        report = {"semantic_merges": [], "duplicates_removed": []}
        for value in values or []:
            item = str(value or "").strip(" ,.")
            if not item:
                continue
            canonical = self._canonical(item)
            if canonical != item:
                report["semantic_merges"].append({"from": item, "to": canonical})
            key = canonical.lower()
            if key in seen:
                report["duplicates_removed"].append(canonical)
                continue
            result.append(canonical)
            seen.add(key)
        return result, report

    def _canonical(self, value):
        lowered = str(value or "").lower()
        for aliases, canonical in self.GROUPS:
            if lowered in aliases or any(alias in lowered for alias in aliases):
                return canonical
        return value

    def _copy_program(self, program):
        copied = {}
        for key, value in (program or {}).items():
            if isinstance(value, dict):
                copied[key] = {
                    nested_key: list(nested_value)
                    if isinstance(nested_value, list)
                    else nested_value
                    for nested_key, nested_value in value.items()
                }
            elif isinstance(value, list):
                copied[key] = list(value)
            else:
                copied[key] = value
        return copied

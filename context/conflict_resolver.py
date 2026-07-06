class ConflictResolver:
    WEAPON_TERMS = (
        "weapon",
        "weapons",
        "sword",
        "blade",
        "combat stance",
        "action scene",
        "weapon showcase",
        "holding a sword",
    )

    def resolve(self, program: dict, forbidden_concepts=None) -> tuple[dict, dict]:
        program = self._copy_program(program)
        forbidden = [str(item).lower() for item in forbidden_concepts or []]
        report = {
            "user_intent_priority": True,
            "removed_conflicts": [],
            "constraints_applied": {},
        }

        if any(term in " ".join(forbidden) for term in ("weapon", "sword", "blade")):
            program.setdefault("constraints", {})["weapon"] = False
            report["constraints_applied"]["weapon"] = False
            self._remove_terms(program, self.WEAPON_TERMS, report)

        for concept in forbidden:
            if concept:
                self._remove_terms(program, (concept,), report)
        return program, report

    def _remove_terms(self, program, terms, report):
        lowered_terms = [term.lower() for term in terms]
        for section, value in list(program.items()):
            if section in {"constraints", "negative"}:
                continue
            if isinstance(value, list):
                kept = []
                for item in value:
                    if self._contains(item, lowered_terms):
                        report["removed_conflicts"].append(
                            {"section": section, "value": item}
                        )
                    else:
                        kept.append(item)
                program[section] = kept
            elif isinstance(value, dict):
                for key, nested in list(value.items()):
                    if isinstance(nested, list):
                        kept = []
                        for item in nested:
                            if self._contains(item, lowered_terms):
                                report["removed_conflicts"].append(
                                    {"section": f"{section}.{key}", "value": item}
                                )
                            else:
                                kept.append(item)
                        program[section][key] = kept
                    elif isinstance(nested, str) and self._contains(nested, lowered_terms):
                        report["removed_conflicts"].append(
                            {"section": f"{section}.{key}", "value": nested}
                        )
                        program[section][key] = ""

    def _contains(self, value, terms):
        lowered = str(value or "").lower()
        return any(term in lowered for term in terms)

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

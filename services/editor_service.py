class EditorService:
    def apply_command(self, variant: dict, command: str) -> dict:
        cmd = command.lower().strip()
        updated = dict(variant)

        if "urgent" in cmd:
            updated["headline"] = f"Now: {updated['headline']}"
        if "background" in cmd and "color" in cmd:
            updated.setdefault("visual", {})["background"] = "#1D4ED8"
        if "professionals" in cmd:
            updated["headline"] = updated["headline"].replace("students", "professionals")
        if "cta" in cmd and "strong" in cmd:
            updated["cta"] = "Act Now"

        return updated

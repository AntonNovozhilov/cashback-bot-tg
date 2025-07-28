def build_post_text(name: str, data: dict) -> str:
    """Формирует итоговый текст поста"""
    lines = []
    tag = "#резюме" if data["post_type"] == "resume" else "#вакансия"
    role = data["role"].capitalize()
    lines.append(f"{tag} {role}\n")
    lines.append(f"{name}\n")
    if data["post_type"] == "resume":
        lines.append("▫️О себе:\n" + data["about_you"])
        lines.append("\n▫️Об услугах:\n" + data["services"])
        lines.append("\n▫️Преимущества и кейсы:\n" + data["cases"])
    else:
        lines.append("▫️О работодателе:\n" + data["about_company"])
        lines.append("\n▫️Описание должности:\n" + data["position"])
        lines.append("\n▫️Требования:\n" + data["requirements"])
    lines.append(f"\n🖊️ Для отклика пиши {data['contact']}")
    return "\n".join(lines)

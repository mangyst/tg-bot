from src.models.models import Unit


def make_profile_card(user: Unit) -> str:
    name = user.name
    width = len(name) - 1
    top = "╔" + "═" * width + "╗"
    mid = f"   👤 {name}"
    bottom = "╚" + "═" * width + "╝"

    return (
        f"{top}\n"
        f"{mid}\n"
        f"{bottom}\n\n"
        f"💪 STR: {user.STR}\n"
        f"🏹 AGI: {user.AGI}\n"
        f"🧠 INT: {user.INT}\n\n"
        f"📊 Points: {user.POINT}\n"
        f"✨ Free Points: {user.FREE_POINT}"
    )


def update_stats(user: Unit) -> str:

    return (
            "╔════════╗\n"
            "   ✅ ОБНОВЛЕНО\n"
            "╚════════╝\n\n"
            f"👤 {user.name}\n\n"
            f"💪 STR: {user.STR}\n"
            f"🏹 AGI: {user.AGI}\n"
            f"🧠 INT: {user.INT}"
    )


def start_challenger(user: Unit) -> str:

    return (
            "╔══════════╗\n"
            "   ⚔️ ВЫЗОВ НА ДУЭЛЬ\n"
            "╚══════════╝\n\n"
            f"👤 {user.name} бросил вызов чату!\n"
            "Кто осмелится принять? 🤔"
    )


def get_winner(user: Unit) -> str:

    return (
        "╔══════╗\n"
        "   🏆 ПОБЕДА!\n"
        "╚══════╝\n\n"
        f"🎉 {user.name} одержал верх в дуэли!"
    )
from src.models.models import Unit


def make_profile_card(user: Unit) -> str:
    name = user.name
    width = len(name) + 3
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
        f"✨ Free Points: {user.FREE_POINT}\n"
        f"🏆 Wins: {user.WIN}\n"
        f"💀 Losses: {user.LOSE}"
    )


def update_stats(user: Unit) -> str:

    return (
            "╔═══════════════╗\n"
            "   ✅ УСПЕХ\n"
            "╚═══════════════╝\n\n"
            f"✨ Твои новые характеристики записаны:\n"
            f"👤 {user.name}\n"
            f"💪 STR: {user.STR}\n"
            f"🏹 AGI: {user.AGI}\n"
            f"🧠 INT: {user.INT}\n\n"
            f"⚔️ Да будут они испытаны в грядущих дуэлях!"
    )


def start_challenger(user: Unit) -> str:

    return (
            "╔════════════════════╗\n"
            "   ⚔️ ВЫЗОВ НА ДУЭЛЬ\n"
            "╚════════════════════╝\n\n"
            f"👤 {user.name} бросил вызов чату!\n"
            "Кто осмелится принять? 🤔"
    )


def get_winner(user_winner: Unit, user_loser: Unit) -> str:

    return (
        "╔═════════════╗\n"
        "   🏆 ПОБЕДА!\n"
        "╚═════════════╝\n\n"
        f"👑 {user_winner.name} доказал своё превосходство!\n"
        f"🕯️ Память о доблести {user_loser.name} будет жить в веках."
    )
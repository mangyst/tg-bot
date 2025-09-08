# Скрипт создания юнита
CREATE_USER_SCRIPT = """
    INSERT INTO users_bot (user_id, user_name, hp, strength, agility, intelligence, point, free_point)
    VALUES (:user_id, :user_name, :hp, :strength, :agility, :intelligence, :point, :free_point)
    RETURNING user_id;
    """

# Скрипт создания юнита
GET_USER_SCRIPT = """
    SELECT *
    FROM users_bot
    WHERE user_id = :user_id;
    """

# Скрипт установки характеристик
SET_STATS_SCRIPT = """
    UPDATE users_bot
    SET
    strength = strength + :added_strength,
    agility = agility + :added_agility,
    intelligence = intelligence + :added_intelligence,
    point = point
    free_point = free_point - :summ_stats
    WHERE user_id = :user_id;
    """

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

# Скрипт сброса характеристик
RESET_STATS_SCRIPT = """
    UPDATE users_bot
    SET
    strength = 0,
    agility = 0,
    intelligence = 0,
    free_point = point
    WHERE user_id = :user_id;
    """

# Скрипт добавления характеристик
ADD_STATS_SCRIPTS = """
    UPDATE users_bot
    SET
    point = point + :f_point,
    free_point = free_point + :f_point
    WHERE user_id = :user_id;
    """

from tg_bot import main as tg_main
from vk_bot import main as vk_main
from bot_functions import get_redis_db, get_questions_and_answers


def main():
    tg_main()
    vk_main()


if __name__ == "__main__":
    r = get_redis_db()
    questions_and_answers = get_questions_and_answers()
    main()

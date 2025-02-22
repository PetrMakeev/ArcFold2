from datetime import datetime, timedelta


def next_run_time(task):
    """
    Вычисляет следующее время запуска задачи по данным из конфигурации.

    :param task: Словарь с параметрами задачи, включая расписание.
                 Формат задачи:
                 {
                     "schedule": "daily" | "weekly" | "monthly" ,
                     "time": "HH:MM",
                     "days": [1, 15, 30],  # Только для monthly
                     "day_of_week": ["Monday", "Sunday"],  # Только для weekly
                 }
    :return: Объект datetime с указанием следующего времени запуска.
    """
    now = datetime.now()

    # Тип расписания
    schedule_type = task["schedule"]

    if schedule_type == "daily":
        # Ежедневное расписание
        task_time = datetime.strptime(task["time"], "%H:%M").time()
        next_run = datetime.combine(now.date(), task_time)

        if next_run <= now:
            # Если текущее время уже прошло, добавляем один день
            next_run += timedelta(days=1)

    elif schedule_type == "weekly":
        # Еженедельное расписание
        day_of_week_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
        task_time = datetime.strptime(task["time"], "%H:%M").time()
        
        list_days = [item.strip() for item in task.get("days_of_week")]
        
        task_days = [day_of_week_map[day.lower()] for day in list_days]

        # Ищем ближайший день недели
        today_weekday = now.weekday()
        days_until_next = [(day - today_weekday) % 7 for day in task_days]
        min_days_until_next = min(days_until_next)
        next_run_date = now.date() + timedelta(days=min_days_until_next)

        next_run = datetime.combine(next_run_date, task_time)

    elif schedule_type == "monthly":
        # Ежемесячное расписание
        task_time = datetime.strptime(task["time"], "%H:%M").time()
        task_days = task["days_of_month"]

        # Проверяем текущий месяц
        current_month = now.month
        current_year = now.year

        # Сортируем дни месяца
        task_days = sorted(task_days)

        for day in task_days:
            try:
                next_run_date = datetime(current_year, current_month, day)
                next_run = datetime.combine(next_run_date, task_time)
                if next_run > now:
                    break
            except ValueError:
                # Пропускаем некорректные дни (например, 30 февраля)
                continue
        else:
            # Если нет подходящих дней в текущем месяце, переходим на следующий
            next_month = (current_month % 12) + 1
            next_year = current_year + (1 if next_month == 1 else 0)
            next_run_date = datetime(next_year, next_month, task_days[0])
            next_run = datetime.combine(next_run_date, task_time)

    elif schedule_type == "one_time":
        # Одноразовое расписание
        next_run = datetime.strptime(task["datetime"], "%Y-%m-%d %H:%M:%S")

        if next_run <= now:
            next_run = None  # Задача уже прошла

    else:
        raise ValueError(f"Unsupported schedule type: {schedule_type}")

    return next_run
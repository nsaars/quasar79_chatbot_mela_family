from typing import Type
from datetime import datetime, timedelta

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, field_validator

from ai.data.config import CONSULTATION_DESCRIPTION


class ConsultationInput(BaseModel):
    date: str = Field(description="Желаемая дата для консультации.", json_schema_extra={'format': '%Y-%m-%d'})
    time: str = Field(description="Желаемое время для консультации.", json_schema_extra={'format': '%H:%M'})

    @field_validator('time')
    @classmethod
    def check_consultation_time(cls, v):
        consultation_time = datetime.strptime(v, '%H:%M')
        if not (13 <= consultation_time.hour <= 18):
            raise ValueError("Консультации проводятся с 13:00 до 18:00. Пожалуйста, выберите другое время.")

        if consultation_time.minute not in (0, 30):
            if consultation_time.minute > 45:
                suggestion_time = consultation_time.replace(minute=0) + timedelta(hours=1)
            elif consultation_time.minute < 15:
                suggestion_time = consultation_time.replace(minute=0)
            else:
                suggestion_time = consultation_time.replace(minute=30)
            raise ValueError(f"Могу записать вас на {suggestion_time.strftime('%H:%M')}, подойдёт?")
        return v

    @field_validator('date')
    @classmethod
    def check_consultation_date(cls, v):
        consultation_time = datetime.strptime(v, '%Y-%m-%d')
        if consultation_time.date() < datetime.now().date():
            raise ValueError("Вы не можете записаться на прошедшую дату. Пожалуйста, выберите будущую дату.")
        if consultation_time.weekday() in (2, 6):
            raise ValueError("Консультации не проводятся по средам и воскресеньям, давайте выберем другой день :)")
        return v

class ConsultationHelpers:

    @staticmethod
    def get_now_date_time():
        months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]
        days_of_week = [
            "понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"
        ]

        now = datetime.now()

        day = now.day
        month = months[now.month - 1]
        year = now.year
        day_of_week = days_of_week[now.weekday()]
        time = now.strftime('%H:%M')

        return f"{day} {month} {year} года, {day_of_week}, {time}"


class ConsultationTool(BaseTool):
    name: str = "schedule_consultation"
    description: str = CONSULTATION_DESCRIPTION.format(current_date_time=ConsultationHelpers.get_now_date_time())
    args_schema: Type[BaseModel] = ConsultationInput
    additionalProperties: bool = False

    def _run(
        self,
        date: str,
        time: str
    ) -> str:
        """Use the tool."""
        try:
            consultation_input = ConsultationInput(date=date, time=time)
            return f"Записал вас на бесплатную консультацию со специалистом на {date} в {time}"
        except ValueError as e:
            return str(e.args[0][0].exc)
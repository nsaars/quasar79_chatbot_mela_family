import re
from pprint import pprint
from typing import Optional, Dict, TypedDict, Tuple

from sqlalchemy.sql.functions import session_user


class Survey:

    def __init__(self, survey_path: str):
        self.survey: Dict = self.parse_survey(survey_path)
        self.current_question_number: int = 1
        self.is_survey_in_process = False
        self.is_answer_changing = False
        self.changing_answer_number = None

    @staticmethod
    def parse_survey(survey_path: str):
        with open(survey_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        headers = {}
        questions = {}
        current_header_number = None

        for line in lines:
            line = line.strip()

            if line.startswith('###'):
                header_parts = line.split(' ', 1)
                if len(header_parts) == 2:
                    current_header_number = int(header_parts[1].split('.')[0].strip())
                    header_title = header_parts[1].split('.', 1)[1].strip()
                    headers[current_header_number] = header_title

            elif line and current_header_number and line[0].isdigit():
                question_number = int(line.split('.')[0])
                question_text = line.split('.', 1)[1].strip()
                questions[question_number] = {
                    'question': question_text,
                    'question_header_number': current_header_number
                }

        return {'headers': headers, 'questions': questions}

    def get_question_by_number(self, question_number) -> Optional[Tuple[int, str]]:
        if question_number in self.survey['questions']:
            return question_number, self.survey['questions'][question_number]['question']
        return

    def get_current_question(self) -> Optional[Tuple[int, str]]:
        return self.get_question_by_number(self.current_question_number)

    def get_next_question(self, update_current_question_number=False) -> Optional[Tuple[int, str]]:
        next_question_number = self.current_question_number + 1
        if update_current_question_number:
            self.current_question_number = next_question_number
        return self.get_question_by_number(next_question_number)

    def get_changing_answer_question(self) -> Optional[Tuple[int, str]]:
        if self.is_answer_changing:
            return self.get_question_by_number(self.changing_answer_number)
        return

    def get_survey_progress(self):
        total_questions = len(self.survey['questions'])

        return {
            'total_questions': total_questions,
            'passed_questions': self.current_question_number - 1,
            'remaining_questions': total_questions - self.current_question_number + 1
        }

    def start_survey(self):
        self.is_survey_in_process = True
        self.current_question_number = 1
        self.is_answer_changing = False
        self.changing_answer_number = None

        #удплить
        with open('answers.txt', 'w', encoding='utf-8') as file:
            file.write(" ")

    def get_start_survey_message(self):
        return "Отлично, давайте приступим к заполнению анкеты для создания вашего уникального личного бренда!\n\nВопрос 1: {question}".format(question=self.survey['questions'][1]['question'])

    def get_next_question_message(self, update_current_question_number=False):
        return "Отлично, принял ваш ответ!\nПриступаем к следующему вопросу\n\nВопрос {0}: {1}".format(*self.get_next_question(update_current_question_number))

    def get_change_answer_message(self, question_number):
        if question_number > self.current_question_number:
            return "Мы ещё не дошли до этого вопроса.", False
        if not 0 < question_number < len(self.survey['questions']):
            return "Я не совсем понял, на какого вопрос вы хотите изменить ответ. Пожалуйста, дайте корректный номер этого вопроса.", False

        return "Хорошо, давайте изменим ответ на вопрос {0}. Вам нужно дать полный ответ, а не дополнять предыдущую информацию.\n\nВопрос {0}: {1}".format(
            *self.get_question_by_number(question_number)), True

    def get_new_answer_set_message(self):
        return "Отлично, принял ваш ответ!\nТеперь давайте вернемся к текущему вопросу\n\nВопрос {0}: {1}".format(*self.get_current_question())

    def get_cancel_changing_answer_message(self):
        return "Хорошо, давайте вернемся к текущему вопросу\n\nВопрос {0}: {1}".format(*self.get_current_question())


    def set_answer(self, question_number, answer):
        if self.get_question_by_number(question_number):
            self.survey['questions'][question_number].update(answer=answer)
            
            # потом удалить
            with open('answers.txt', 'a', encoding='utf-8') as file:
                text = f"Вопрос {question_number}\nОтвет:\t{answer}\n\n"
                file.write(text)

if __name__ == '__main__':
    survey = Survey('survey.txt')
    pprint(survey.survey)

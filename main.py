
from scripts.variable_handling import CualitativeSurvey
from pathlib import Path
import time


def main():
    my_survey = CualitativeSurvey(filename="prueba_vacia", p_id="001")
    my_survey.init_csv()
    responses = my_survey.ask_survey()
    my_survey.save_survey_response(responses)

    print("Survey Cualitativa Finalizada.")

if __name__ == "__main__":
    main()


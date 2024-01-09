PYTHON_INTERPRETER = python3
CONDA_ENV ?= speech-ai-azure-services
export PYTHONPATH=$(PWD):$PYTHONPATH;

# Target for setting up pre-commit and pre-push hooks
set_up_precommit_and_prepush:
	pre-commit install -t pre-commit
	pre-commit install -t pre-push

# The 'check_code_quality' command runs a series of checks to ensure the quality of your code.
check_code_quality:
	# Running 'ruff' to automatically fix common Python code quality issues.
	@pre-commit run ruff --all-files

	# Running 'black' to ensure consistent code formatting.
	@pre-commit run black --all-files

	# Running 'isort' to sort and organize your imports.
	@pre-commit run isort --all-files

	# # Running 'flake8' for linting.
	@pre-commit run flake8 --all-files

	# Running 'mypy' for static type checking.
	@pre-commit run mypy --all-files

	# Running 'check-yaml' to validate YAML files.
	@pre-commit run check-yaml --all-files

	# Running 'end-of-file-fixer' to ensure files end with a newline.
	@pre-commit run end-of-file-fixer --all-files

	# Running 'trailing-whitespace' to remove unnecessary whitespaces.
	@pre-commit run trailing-whitespace --all-files

	# Running 'interrogate' to check docstring coverage in your Python code.
	@pre-commit run interrogate --all-files

	# Running 'bandit' to identify common security issues in your Python code.
	bandit -c pyproject.toml -r .

fix_code_quality:
	# Automatic fixes for code quality (not doing in production only dev cycles)
	black .
	isort .
	ruff --fix .

# Targets for running tests
run_unit_tests:
	$(PYTHON_INTERPRETER) -m pytest --cov=my_module --cov-report=term-missing --cov-config=.coveragerc

check_and_fix_code_quality: fix_code_quality check_code_quality
check_and_fix_test_quality: run_unit_tests

# Targets for various operations and tests

# Colored text
RED = \033[0;31m
NC = \033[0m # No Color
GREEN = \033[0;32m

# Helper function to print section titles
define log_section
	@printf "\n${GREEN}--> $(1)${NC}\n\n"
endef

run_pylint:
	@echo "Running linter"
	find . -type f -name "*.py" ! -path "./tests/*" | xargs pylint -disable=logging-fstring-interpolation > utils/pylint_report/pylint_report.txt

create_conda_env:
	@echo "Creating conda environment"
	conda env create -f environment.yaml

test_speech_to_text_raw_file: 
	@echo "Runnng speech to text services using Azure AI speech services"
	$(PYTHON_INTERPRETER) $(PWD)/src/speech_sdk/speech_to_text.py --file $(PWD)\utils\audio_data\d6a35a5e-be01-40cd-b9ef-d61fcda699fa.wav

test_speech_to_text_intent_lenguage: 
	@echo "Runnig speech to text services and intent recognition Azure AI lengauge understanding"
	$(PYTHON_INTERPRETER) $(PWD)/src/speech_sdk/intent_from_lenguage.py --file $(PWD)\utils\audio_data\d6a35a5e-be01-40cd-b9ef-d61fcda699fa.wav
	@echo "Done"

test_speech_to_text_intent_azure_openai: 
	@echo "Running Speech-to-Text services and Intent Recognition using Azure Open AI GPT-3.5 models"
	$(PYTHON_INTERPRETER) $(PWD)/src/aoai/intent_azure_openai.py --file $(PWD)\utils\audio_data\d6a35a5e-be01-40cd-b9ef-d61fcda699fa.wav
	@echo "Done"

demo_app_speech_to_text_to_speech:
	@echo "Running app with full end-to-end capability to recognize speech from microphone, process NLU and NLG with Azure Open AI gpt4, and generate speech response with Azure AI speech service"
	$(PYTHON_INTERPRETER) $(PWD)/src/demo_app.py
	@echo "Done"

run_app:
	@echo "Running streamlit app with full end-to-end capability to recognize speech from microphone"
	streamlit run $(PWD)/src/app/Home.py
	@echo "Done"

delete_old_folders: 
	@echo "Deleting old folders"
	$(PYTHON_INTERPRETER) $(PWD)/utils/batch_delete.py --base_path $(PWD)\src\app\uploads --days_threshold 0
	@echo "Done"

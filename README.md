# <img src="./utils/images/azure_logo.png" alt="Azure Logo" style="width:30px;height:30px;"/> Quickstart Guide: Azure AI Speech Services (Preview)

This project is a comprehensive guide to leveraging advanced AI services from Azure. It provides a hands-on approach to understanding and implementing the following services:

- **Azure AI Speech Services**: This service offers robust capabilities for converting speech to text and text to speech. It uses Azure's cutting-edge speech recognition technology, which is trained on a wide range of data from various domains to ensure high accuracy across different scenarios. You can learn more about this in the [01-speech-to-text.ipynb](01-speech-to-text.ipynb) notebook.

- **Azure AI Language Understanding**: This service allows you to build applications that can understand user commands contextually. The project guides you on how to use intent recognition to derive meaningful insights from speech, enabling more natural interactions with your applications using Azure AI lenguage and Open AI models. Explore this in the [02-intent-recognition.ipynb](02-intent-recognition.ipynb) notebook.

- **Azure OpenAI GPT-4 (turbo) and GPT-3.5**: These models offer advanced natural language processing and understanding capabilities. The project provides detailed steps on how to integrate these models into your applications to build sophisticated AI agents that can understand prompts, provide detailed responses, and even generate human-like text. Dive into this topic in the [03-conversational-ai-agents.ipynb](03-conversational-ai-agents.ipynb) notebook.

By following this project, you'll gain practical knowledge on how to integrate these powerful Azure AI services into your own applications. Start with the first notebook and work your way through. Happy learning!

#### 🔄 Demo Application: Speech-to-Text-to-Speech

Demonstrates an end-to-end application that recognizes speech, processes it using Azure OpenAI GPT-4 for NLU and NLG, and generates a speech response with Azure AI Speech Service.

```bash
make demo_app_speech_to_text_to_speech
```

## 🔧 Prerequisites 

Please make sure you have met all the prerequisites for this project. A detailed guide on how to set up your environment and get ready to run all the notebooks and code in this repository can be found in the [REQUIREMENTS.md](REQUIREMENTS.md) file. Please follow the instructions there to ensure a smooth exprience.


## 💼 Contributing

Eager to make significant contributions? Our **[CONTRIBUTING](./CONTRIBUTING.md)** guide is your essential resource! It lays out a clear path for:

- To stay updated with the latest developments and document significant changes to this project, please refer to [CHANGELOG.md](CHANGELOG.md).

## 🌲 Project Tree Structure

```
📂 gbbai-azure-ai-speech-services
┣ 📂 notebooks <- For development, and quick testing 
┣ 📦 src <- Houses main source code for speach_sdk examples.
┣ 📂 test <- Runs unit and integration tests for code validation and QA.
┣ 📂 utils <- Contains utility functions and shared code used throughout the project. Detailed info in README
┣ 📜 .pre-commit-config.yaml <- Config for pre-commit hooks ensuring code quality and consistency.
┣ 📜 01-speech-to-text.ipynb
┣ 📜 02-intent-recognition.ipynb
┣ 📜 03-conversational-ai-agents.ipynb
┣ 📜 CHANGELOG.md <- Logs project changes, updates, and version history.
┣ 📜 CONTRIBUTING.md <- Guidelines for contributing to the project.
┣ 📜 environment.yaml <- Conda environment configuration.
┣ 📜 Makefile <- Simplifies common development tasks and commands.
┣ 📜 pyproject.toml <- Configuration file for build system requirements and packaging-related metadata.
┣ 📜 README.md <- Overview, setup instructions, and usage details of the project.
┣ 📜 requirements-codequality.txt <- Requirements for code quality tools and libraries.
┣ 📜 requirements.txt <- General project dependencies.
```



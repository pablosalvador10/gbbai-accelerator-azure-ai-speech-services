# Azure AI speech services GBB AI Accelerator (preview) <img src="./utils/images/azure_logo.png" alt="Azure Logo" style="width:30px;height:30px;"/>

Welcome to the a GBB AI Quick Start Accelerator! 

This project leverages advanced AI services from Azure, including Azure AI Speech Services, Azure OpenAI GPT-4, and Azure AI Language Understanding. It includes scripts for:
- Speech-to-text conversions using Azure's cutting-edge speech recognition.
- Intent recognition utilizing Azure Language Understanding to derive meaningful insights from speech.
- Integration with Azure OpenAI GPT-4 for advanced natural language processing and understanding.

## 🌟 Goal
The primary goal of this Accelerator is to provide a quick start for developing complex AI solutions using Azure AI services. It acts as a comprehensive guide for both novices and seasoned professionals, enabling the efficient establishment, deployment, and management of sophisticated AI systems.

## Prerequisites 

### 🔧 Dependencies

#### Azure Services
- Azure OpenAI Service: You need to create an Azure OpenAI service instance and obtain the API key.
- Azure Speech AI Service: Required for speech-to-text conversion. Set up the service and get the subscription key and region.
- Azure Language Service: Necessary for language understanding and intent recognition.

#### Environment Variables
Add the following keys to your `.env` file (see `.env.sample`)

#### System Requirements

Please follow https://github.com/Azure-Samples/cognitive-services-speech-sdk/tree/master/quickstart/python/from-microphone

### 🛠 Getting Started

In this project, `make` is utilized to automate the execution of scripts, significantly streamlining the development process.

#### Why Use `make`?

`make` is a powerful build automation tool traditionally used in software development for automating the compilation of executable programs and libraries. It works by reading files called `Makefiles` which define how to build and run tasks.

#### 🌐 Create Conda Environment

```bash
make create_conda_env
```

#### 🎤 Test Speech to Text with Raw File

Utilizes Azure AI Speech Services to convert speech in a .wav file to text.

```bash
make test_speech_to_text_raw_file
```

#### 🧠 Test Speech to Text with Intent Recognition (Azure AI Language Understanding)

Employs Azure AI Language Understanding for intent recognition in speech-to-text conversion.

```bash
make test_speech_to_text_intent_lenguage
```

#### 💡 Test Speech to Text with Intent Recognition (Azure OpenAI GPT-4)

Integrates Azure OpenAI GPT-4 for sophisticated intent recognition and natural language understanding in speech-to-text processes.

```bash
make test_speech_to_text_intent_openai
```

#### 🔄 Demo Application: Speech-to-Text-to-Speech

Demonstrates an end-to-end application that recognizes speech, processes it using Azure OpenAI GPT-4 for NLU and NLG, and generates a speech response with Azure AI Speech Service.

```bash
make demo_app_speech_to_text_to_speech
```


## 💼 Contributing

Eager to make significant contributions? Our **[CONTRIBUTING](./CONTRIBUTING.md)** guide is your essential resource! It lays out a clear path for:

- To stay updated with the latest developments and document significant changes to this project, please refer to [CHANGELOG.md](CHANGELOG.md).

## 🌲 Project Tree Structure

```
📂 gbbai-accelerator-azure-ai-speech-services
┣ 📂 notebooks <- For development, and quick testing 
┣ 📦 src <- Houses main source code for speach_sdk examples.
┣ 📂 test <- Runs unit and integration tests for code validation and QA.
┣ 📂 utils <- Contains utility functions and shared code used throughout the project. Detailed info in README
┣ 📜 .pre-commit-config.yaml <- Config for pre-commit hooks ensuring code quality and consistency.
┣ 📜 CHANGELOG.md <- Logs project changes, updates, and version history.
┣ 📜 CONTRIBUTING.md <- Guidelines for contributing to the project.
┣ 📜 environment.yaml <- Conda environment configuration.
┣ 📜 Makefile <- Simplifies common development tasks and commands.
┣ 📜 pyproject.toml <- Configuration file for build system requirements and packaging-related metadata.
┣ 📜 README.md <- Overview, setup instructions, and usage details of the project.
┣ 📜 requirements-codequality.txt <- Requirements for code quality tools and libraries.
┣ 📜 requirements-pipelines.txt <- Requirements for pipeline-related dependencies.
┣ 📜 requirements.txt <- General project dependencies.
```



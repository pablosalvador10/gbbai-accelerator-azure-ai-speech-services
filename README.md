# <img src="./utils/images/azure_logo.png" alt="Azure Logo" style="width:30px;height:30px;"/> Quickstart Guide: Azure AI Speech Services (Preview)

This project is a comprehensive guide to leveraging advanced AI services from Azure. It provides a hands-on approach to understanding and implementing the following services:

- **Azure AI Speech Services**: This service offers robust capabilities for converting speech to text and text to speech. It uses Azure's cutting-edge speech recognition technology, which is trained on a wide range of data from various domains to ensure high accuracy across different scenarios.

- **Azure AI Language Understanding**: This service allows you to build applications that can understand user commands contextually. The project guides you on how to use intent recognition to derive meaningful insights from speech, enabling more natural interactions with your applications.

- **Azure OpenAI GPT-4 (turbo) and GPT-3.5**: These models offer advanced natural language processing and understanding capabilities. The project provides detailed steps on how to integrate these models into your applications to build sophisticated AI agents that can understand prompts, provide detailed responses, and even generate human-like text.

By following this project, you'll gain practical knowledge on how to integrate these powerful Azure AI services into your own applications.

## 🔧 Prerequisites 

### Setting Up Azure AI Services

- Azure OpenAI Service: You need to create an Azure OpenAI service instance and obtain the API key. [start here](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- Azure Speech AI Service: Required for speech-to-text conversion. Set up the service and get the subscription key and region. [start here](https://azure.microsoft.com/en-us/products/ai-services/ai-speech)
- Azure Language Service: Necessary for language understanding and intent recognition.[start here](https://azure.microsoft.com/en-us/products/ai-services/ai-language)

### Configuration Env variables

We will now use environment variables to store our configuration. This is a more secure practice as it prevents sensitive data from being accidentally committed and pushed to version control systems.

Create a `.env` file in your project root and add the following variables:

```env
# Your Azure Speech Service subscription key
SPEECH_KEY=<Your_Azure_Speech_Service_Subscription_Key>

# Your Azure Speech Service region
SPEECH_REGION=<Your_Azure_Speech_Service_Region>

# Your Azure Machine Learning workspace key
INTENT_KEY=<Your_Azure_Machine_Learning_Workspace_Key>

# Your Azure OpenAI API key
OPENAI_KEY=<Your_Azure_OpenAI_API_Key>

# The model used for chat
CHAT_MODEL=<Your_Chat_Model>

# The model used for completions
COMPLETION_MODEL=<Your_Completion_Model>

# The base URL for the OpenAI API
OPENAI_API_BASE=<Your_OpenAI_API_Base_URL>

# The version of the OpenAI API
OPENAI_API_VERSION=<Your_OpenAI_API_Version>

# Your Azure Storage connection string
AZURE_STORAGE_CONNECTION_STRING=<Your_Azure_Storage_Connection_String>
``` 

`SPEECH_KEY` and `SPEECH_REGION` are used for the Azure Speech Service.
`INTENT_KEY` is used for the Azure Machine Learning workspace.
`OPENAI_KEY`, `CHAT_MODEL`, `COMPLETION_MODEL`, `OPENAI_API_BASE`, and `OPENAI_API_VERSION` are used for the Azure OpenAI API.
`AZURE_STORAGE_CONNECTION_STRING` is used for Azure Storage.

> 📌 Note Remember not to commit the .env file to your version control system. Add it to your .gitignore file to prevent it from being tracked.

### System Requirements

#### Setting Up Microphone Speech Recognition 🎤

Before you dive in, ensure you have the following prerequisites:

- A subscription key for the Speech service. You can get a free trial [here](https://azure.microsoft.com/en-us/try/cognitive-services/?api=speech-services).
- Python 3.6 or later installed. For Mac users, the minimum Python version is 3.7. You can download Python [here](https://www.python.org/downloads/).
- The Python Speech SDK package. It's available for Windows (x64 and x86), Mac x64 (macOS X version 10.14 or later), Mac arm64 (macOS version 11.0 or later), and specific Linux distributions and target architectures.

Depending on your operating system, follow the instructions below:

##### Ubuntu or Debian
Run the following commands to install the required packages:

```bash
sudo apt-get update
sudo apt-get install libssl-dev libasound2
```
For Ubuntu 22.04 LTS, you also need to download and install the latest libssl1.1 package from [here](http://security.ubuntu.com/ubuntu/pool/main/o/openssl/.).

##### RHEL or CentOS
Run the following commands to install the required packages:

```bash
sudo yum update
sudo yum install alsa-lib openssl python3
```
See also how to configure RHEL/CentOS 7 for Speech SDK [here](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-configure-rhel-centos-7).

##### Windows 

You need the Microsoft Visual C++ Redistributable for Visual Studio 2017 for your platform. 

More details (here) [https://github.com/Azure-Samples/cognitive-services-speech-sdk/tree/master/quickstart/python/from-microphone]

## 🚀 Quick Start Guide

This project includes several Jupyter notebooks that serve as interactive tutorials for different aspects of Azure's AI Services. Here's a brief overview of each notebook:

- [01-speech-to-text.ipynb](01-speech-to-text.ipynb): Learn how to convert spoken language into written text using Azure's AI Speech Services. This step-by-step guide will walk you through the process, from setting up the service to implementing it in your applications.

- [02-intent-recognition.ipynb](02-intent-recognition.ipynb): Explore the world of intent recognition. This tutorial dives deep into how you can use Azure's AI Services to understand the purpose or goal behind spoken commands, enabling more natural interactions with your applications.

- [03-conversational-ai-agents.ipynb](03-conversational-ai-agents.ipynb): Get introduced to conversational AI agents. This guide showcases how you can leverage Azure's advanced natural language processing and understanding capabilities to build sophisticated AI agents that can engage in human-like conversations. (#TODO)

Start with the first notebook and work your way through. Happy learning!

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



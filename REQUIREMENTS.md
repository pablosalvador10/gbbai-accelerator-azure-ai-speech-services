## Table of Contents

- [Setting Up Azure AI Services](#setting-up-azure-ai-services)
- [Configuration Environment Variables](#configuration-environment-variables)
- [System Requirements](#system-requirements)
  - [Setting Up Microphone Speech Recognition](#setting-up-microphone-speech-recognition)
- [Notebooks Setup](#notebooks-setup)
  - [Setting Up Conda Environment and Configuring VSCode for Jupyter Notebooks](#setting-up-conda-environment-and-configuring-vscode-for-jupyter-notebooks)

## Setting Up Azure AI Services

- Azure OpenAI Service: Create an Azure OpenAI service instance and obtain the API key. [Start here](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- Azure Speech AI Service: Required for speech-to-text conversion. Set up the service and get the subscription key and region. [Start here](https://azure.microsoft.com/en-us/products/ai-services/ai-speech)
- Azure Language Service: Necessary for language understanding and intent recognition. [Start here](https://azure.microsoft.com/en-us/products/ai-services/ai-language)

## Configuration Environment Variables

Store your configuration in environment variables to prevent sensitive data from being accidentally committed and pushed to version control systems. Create a `.env` file in your project root and add the following variables:

```env
SPEECH_KEY=<Your_Azure_Speech_Service_Subscription_Key>
SPEECH_REGION=<Your_Azure_Speech_Service_Region>
INTENT_KEY=<Your_Azure_Machine_Learning_Workspace_Key>
OPENAI_KEY=<Your_Azure_OpenAI_API_Key>
CHAT_MODEL=<Your_Chat_Model>
COMPLETION_MODEL=<Your_Completion_Model>
OPENAI_API_BASE=<Your_OpenAI_API_Base_URL>
OPENAI_API_VERSION=<Your_OpenAI_API_Version>
AZURE_STORAGE_CONNECTION_STRING=<Your_Azure_Storage_Connection_String>
``` 

`SPEECH_KEY` and `SPEECH_REGION` are used for the Azure Speech Service.
`INTENT_KEY` is used for the Azure Machine Learning workspace.
`OPENAI_KEY`, `CHAT_MODEL`, `COMPLETION_MODEL`, `OPENAI_API_BASE`, and `OPENAI_API_VERSION` are used for the Azure OpenAI API.
`AZURE_STORAGE_CONNECTION_STRING` is used for Azure Storage.

> 📌 Note Remember not to commit the .env file to your version control system. Add it to your .gitignore file to prevent it from being tracked.

## System Requirements

### Setting Up Microphone Speech Recognition 🎤

Before you dive in, ensure you have the following prerequisites:

- A subscription key for the Speech service. You can get a free trial [here](https://azure.microsoft.com/en-us/try/cognitive-services/?api=speech-services).
- Python 3.6 or later installed. For Mac users, the minimum Python version is 3.7. You can download Python [here](https://www.python.org/downloads/).
- The Python Speech SDK package. It's available for Windows (x64 and x86), Mac x64 (macOS X version 10.14 or later), Mac arm64 (macOS version 11.0 or later), and specific Linux distributions and target architectures.

Depending on your operating system, follow the instructions below:

#### Ubuntu or Debian
Run the following commands to install the required packages:

```bash
sudo apt-get update
sudo apt-get install libssl-dev libasound2
```
For Ubuntu 22.04 LTS, you also need to download and install the latest libssl1.1 package from [here](http://security.ubuntu.com/ubuntu/pool/main/o/openssl/.).

#### RHEL or CentOS
Run the following commands to install the required packages:

```bash
sudo yum update
sudo yum install alsa-lib openssl python3
```
See also how to configure RHEL/CentOS 7 for Speech SDK [here](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-configure-rhel-centos-7).

#### Windows 

You need the Microsoft Visual C++ Redistributable for Visual Studio 2017 for your platform. 

More details (here)[https://github.com/Azure-Samples/cognitive-services-speech-sdk/tree/master/quickstart/python/from-microphone]

## 🛠️ Notebooks Setup 

### Setting Up Conda Environment and Configuring VSCode for Jupyter Notebooks

Follow these steps to create a Conda environment and set up your VSCode for running Jupyter Notebooks:

#### Create Conda Environment from the Repository

> Instructions for Windows users: 

1. **Create the Conda Environment**:
   - In your terminal or command line, navigate to the repository directory.
   - Execute the following command to create the Conda environment using the `environment.yaml` file:
     ```bash
     conda env create -f environment.yaml
     ```
   - This command creates a Conda environment as defined in `environment.yaml`.

2. **Activating the Environment**:
   - After creation, activate the new Conda environment by using:
     ```bash
     conda activate speech-ai-azure-services
     ```

> Instructions for Linux users (or Windows users with WSL or other linux setup): 

1. **Use `make` to Create the Conda Environment**:
   - In your terminal or command line, navigate to the repository directory and look at the Makefile.
   - Execute the `make` command specified below to create the Conda environment using the `environment.yaml` file:
     ```bash
     make create_conda_env
     ```

2. **Activating the Environment**:
   - After creation, activate the new Conda environment by using:
     ```bash
     conda activate speech-ai-azure-services
     ```

#### Configure VSCode for Jupyter Notebooks

1. **Install Required Extensions**:
   - Download and install the `Python` and `Jupyter` extensions for VSCode. These extensions provide support for running and editing Jupyter Notebooks within VSCode.

2. **Attach Kernel to VSCode**:
   - After creating the Conda environment, it should be available in the kernel selection dropdown. This dropdown is located in the top-right corner of the VSCode interface.
   - Select your newly created environment (`speech-ai-azure-services`) from the dropdown. This sets it as the kernel for running your Jupyter Notebooks.

3. **Run the Notebook**:
   - Once the kernel is attached, you can run the notebook by clicking on the "Run All" button in the top menu, or by running each cell individually.

4. **Voila! Ready to Go**:
   - Now that your environment is set up and your kernel is attached, you're ready to go! Please visit the notebooks in the repository to start exploring.

> **Note:** By following these steps, you'll establish a dedicated Conda environment for your project and configure VSCode to run Jupyter Notebooks efficiently. This environment will include all the necessary dependencies specified in your `environment.yaml` file. If you wish to add more packages or change versions, please use `pip install` in a notebook cell or in the terminal after activating the environment, and then restart the kernel. The changes should be automatically applied after the session restarts.
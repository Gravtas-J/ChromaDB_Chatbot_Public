# MindTrack-Interactive-Journal

MindTrack is an advanced interactive and reflective journaling system designed to assist mental health professionals in tracking their patients' progress. The core functionality of this system revolves around an AI agent which serves dual roles: Conversation and Evaluation.

## Setup

1. Install chromadb and openai (in `requirements.txt` file)
2. Copy `user_profile_template.md`, rename it `user_profile.md`
3. Copy .env.template and save as `.env` with your OpenAI API key

## Usage

- Main chat client: `python chat.py`
- GUI chat client: `GUI.py`
- Evaluation GUI: `eval.py`
- Take a look in your KB: `python chromadb_peek.py`

Features
1. AI Agent
The AI agent is the heart of MindTrack. It operates in two distinct modes:

Conversation Mode: In this mode, the AI agent engages with the user, fostering an interactive and reflective journaling experience. This mode is particularly useful for patients to articulate their feelings, thoughts, and daily experiences.

Evaluation Mode: Leveraging advanced machine learning algorithms, in this mode, the AI agent assesses the patient's progress based on their journal entries. It offers insights and trends that can be invaluable for mental health professionals to understand the trajectory of their patient's mental health journey.

2. Progress Tracking
By combining both the conversational and evaluative capabilities of the AI agent, MindTrack offers a comprehensive progress tracking tool. This empowers mental health professionals to have a more detailed, data-driven approach to understanding and guiding their patient's progress.

#Future Functionality Goals 
System Prompt: The system will initially prompt the user to decide if they wish to engage in a conversational journaling session or if they want to evaluate their progress. Depending on this choice, the AI agent will operate in either Conversation Mode or Evaluation Mode.

Conversation Mode: Engage in a two-way interaction with the AI. The user can document their feelings, thoughts, and experiences, with the AI offering responsive and reflective feedback.

Evaluation Mode: The AI will assess and analyze the past journal entries to offer insights, trends, and a general overview of the patient's progress. This data can then be reviewed by mental health professionals for a more informed approach to treatment.

## Contributing

You're welcome to submit a pull request to make mild changes or fix bugs. Any substantial refactors will be rejected. If you want to take this work and modify it, please just work on your own fork. This repo will eventually be made a public readonly archive. 

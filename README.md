# Healthcare Chatbot System

A complete healthcare chatbot application with patient registration and medical document Q&A capabilities.

## Features

### Flow Chat
- Step-by-step patient registration
- Real-time field validation
- Automatic BMI calculation
- Health status assessment
- Data persistence in JSON format

### RAG Chat
- Medical document query system
- AI-powered responses
- Source document display
- Chat history tracking
- Automatic vector store initialization

## Requirements

```
streamlit
pydantic
pydantic-settings
langchain
langchain-community
langchain-groq
langchain-unstructured
langchain-huggingface
sentence-transformers
faiss-cpu
unstructured
python-dotenv
```

## Installation

```bash
pip install -r requirements.txt
```

## Project Structure

```
project/
├── main.py                 # Home page
├── pages/
│   ├── 1_Flow_Chat.py     # Patient registration
│   └── 2_RAG_Chat.py      # Document Q&A
├── documents/             # Medical documents folder
├── patient_data/          # Saved patient records
├── faiss_index/           # Vector database
├── .env                   # API keys
└── requirements.txt
```

## Setup

1. Create a `.env` file with your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

2. Add medical documents to the `documents/` folder (txt, pdf, or docx files)

3. Run the application:
```bash
streamlit run main.py
```

## Usage

### Flow Chat
1. Navigate to Flow Chat from the sidebar
2. Answer each question step by step
3. Review the summary with BMI and health status
4. Save the patient data to JSON file

### RAG Chat
1. Navigate to RAG Chat from the sidebar
2. Click "Initialize System" to load documents
3. Ask questions about the medical documents
4. View source documents for each answer

## Data Storage

Patient data is stored in `patient_data/patients.json` with the following structure:

```json
[
  {
    "session_id": "unique-id",
    "timestamp": "2025-10-01T14:30:00",
    "patient": {
      "name": "John Doe",
      "age": 35,
      "mobile": "1234567890",
      "email": "john@example.com",
      "blood_group": "O+",
      "height": 1.75,
      "weight": 70,
      "bmi": 22.86,
      "verdict": "Normal"
    }
  }
]
```

## Notes

- The RAG system automatically loads existing vector stores on startup
- Patient data validation happens at each step
- BMI is calculated using the formula: weight / (height²)
- Health status categories: UnderWeight (<18.5), Normal (18.5-25), Overweight (25-30), Obese (>30)

## Troubleshooting

If RAG Chat fails to initialize:
- Check that the `documents/` folder exists and contains files
- Verify your Groq API key in the `.env` file
- Delete the `faiss_index/` folder and reinitialize

If Flow Chat validation fails:
- Name must be at least 2 characters
- Age must be between 1-120
- Mobile must be exactly 10 digits
- Email must contain @ and .
- Height and weight must be greater than 0
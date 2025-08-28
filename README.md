# PDF Content Analyzer and Summarizer

A powerful Python application that uses Langchain to automatically process PDF files, categorizes content, generate summaries, and extract actionable insights. The tool intelligently identifies different types of content (tasks, stories, technical documents, etc.) and formats the output accordingly.

## Features

- 📄 **PDF Processing**: Automatically loads and processes all PDF files from a specified folder
- 🤖 **AI-Powered Analysis**: Uses OpenAI's GPT models via Langchain for intelligent content analysis
- 📊 **Content Categorization**: Automatically categorizes content as tasks, stories, technical document, reports, and so on...
- 📝 **Smart Summarization**: Generates summaries based on content type
- ✅ **Task Extraction**: Identifies and formats action items as bullet-point task lists
- 📚 **Story Analysis**: Extracts characters, themes, and plot summaries from narrative content
- 🔍 **Vector Search**: Creates searchable vector embeddings for future similarity searches
- 📈 **Detailed Reports**: Generates both JSON and Markdown reports

## Installation

1. **Clone this project**
   ```bash
   git clone <repository-url>
   cd pdf-summarization
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   nano .env
   ```

   Or set it directly as an environment variable:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

### Basic Usage

1. **Add PDF files** to the `pdf-inputs` folder
2. **Run the analyzer**:
   ```bash
   python main.py
   ```

The program will:
- Process all PDF files in the `pdf-inputs` folder
- Analyze and categorize the content
- Generate summaries based on content type
- Save results to the `outputs` folder

### Output Files

The program generates two types of output files in the `outputs` folder:

1. **JSON Report** (`analysis_results_YYYYMMDD_HHMMSS.json`)
   - Complete structured data with all analysis results
   - Machine-readable format for further processing

2. **Markdown Report** (`summary_report_YYYYMMDD_HHMMSS.md`)
   - More readable formatted report
   - Organized sections for different content types
   - Task lists with checkboxes
   - Story summaries with characters and themes

## Configuration

### Environment Variables

You can customize the behavior using environment variables in your `.env` file:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional customizations
OPENAI_MODEL=gpt-3.5-turbo-instruct
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=2000
PDF_INPUT_FOLDER=pdf-inputs
OUTPUT_FOLDER=outputs
```

## Example Output

### Task Document Analysis
```markdown
## 📋 Task Lists

### project_requirements.pdf
**Urgency:** high

**Action Item:**
- [ ] Complete user authentication sytem
- [ ] Implement database schema
- [ ] Write unit test for API endpoints
- [ ] Deploy to staging environment

**Summary:**
Project requirements document outlining the development tasks for the Q4 release...
```

### Story Analysis
```markdown
## 📚 Stories

### short_story.pdf
**Character:** Alice, Bob...
**Themes:** adventure, fantasy

**Summary:**
A compelling tale about two friends who discover a mysterious artifact...
```

## Dependencies

- **langchain**: Framework for building LLM applications
- **openai**: OpenAI API client
- **pypdf**: PDF reading and processing
- **faiss-cpu**: Vector similarity search
- **tiktoken**: Token counting for OpenAI models
- **python-dotenv**: Environment variable management

## API Costs

This tool uses OpenAI's API, which incurs costs based on usage:
- Text analysis and summarization use the configured model (default: gpt-3.5-turbo-instruct)
- Embeddings use OpenAI's embedding model
- Costs depend on document length and number of files processed
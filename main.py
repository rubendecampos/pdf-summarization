"""
===========================================================
Project Name: PDF Content Analyzer and Summarizer
Description : Uses Langchain to process PDF, categorizes 
    content, and generates summaries
Author      : Ruben De Campos
Date        : 2025-03-10
License     : MIT License
===========================================================
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime
from dotenv import load_dotenv

# Langchain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document

# Load .env file
load_dotenv()

class PDFAnalyzer:
    def __init__(self, input_folder: str = "pdf-inputs", output_folder: str = "outputs"):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.docs = []
        self.vectorstore = None
        
        # Initialize LLM and embeddings
        self.llm = OpenAI(temperature=0.3)
        self.embeddings = OpenAIEmbeddings()
        
        # Make sure folders exist
        self.input_folder.mkdir(exist_ok=True)
        self.output_folder.mkdir(exist_ok=True)
        
        # For splitting large text into manageable chunks
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
    def load_pdfs(self) -> List[Document]:
        pdf_files = list(self.input_folder.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {self.input_folder}")
            return []
        
        all_docs = []
        for pdf_file in pdf_files:
            try:
                print(f"Loading {pdf_file.name}...")
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                
                # Add metadata about source file
                for doc in docs:
                    doc.metadata['source_file'] = pdf_file.name
                    doc.metadata['file_path'] = str(pdf_file)
                
                all_docs.extend(docs)
                
            except Exception as e:
                print(f"Error loading {pdf_file.name}: {str(e)}")
                continue
        
        self.docs = all_docs
        return all_docs
    
    def create_vectorstore(self):
        if not self.docs:
            print("No docs loaded. Please load PDFs first.")
            return
        
        print("Creating vector store...")
        # Split docs into chunks
        texts = self.text_splitter.split_documents(self.docs)
        
        # Create vector store
        self.vectorstore = FAISS.from_documents(texts, self.embeddings)
    
    def categorize_content(self, text: str) -> Dict[str, Any]:
        categorization_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
            Analyze the following text and categorize it. Determine:
            1. Content type (task, story, technical document, report, etc.)
            2. Main topics/themes
            3. Key entities (people, organizations)
            4. Urgency level (if applicable)
            5. Action items or tasks (if any)
            
            Text: {text}
            
            Provide your analysis in the following JSON format:
            {{
                "content_type": "type of content",
                "main_topics": ["topic1", "topic2"],
                "key_entities": ["entity1", "entity2"],
                "urgency_level": "low/medium/high/none",
                "action_items": ["action1", "action2"],
                "summary": "brief summary of the content"
            }}
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=categorization_prompt)
        
        try:
            result = chain.run(text=text[:3000])  # Limit text length for API
            # Try to parse as JSON, fallback to text if parsing fails
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {"raw_analysis": result}
        except Exception as e:
            print(f"Error in categorization: {str(e)}")
            return {"error": str(e)}
    
    def generate_summary(self, text: str, content_type: str = "general") -> str:
        if content_type.lower() in ["task", "action", "todo"]:
            summary_prompt = PromptTemplate(
                input_variables=["text"],
                template="""
                Create a task-oriented summary of the following text. Focus on:
                - Action items and tasks
                - Deadlines and priorities
                - Responsible parties
                - Dependencies
                
                Format as bullet points with clear action items.
                
                Text: {text}
                
                Task Summary:
                """
            )
        elif content_type.lower() in ["story", "narrative", "fiction"]:
            summary_prompt = PromptTemplate(
                input_variables=["text"],
                template="""
                Create a story summary of the following text. Include:
                - Main characters
                - Plot summary
                - Key themes
                - Setting
                
                Text: {text}
                
                Story Summary:
                """
            )
        else:
            summary_prompt = PromptTemplate(
                input_variables=["text"],
                template="""
                Create a comprehensive summary of the following text. Include:
                - Main points and key information
                - Important details
                - Conclusions or outcomes
                
                Text: {text}
                
                Summary:
                """
            )
        
        chain = LLMChain(llm=self.llm, prompt=summary_prompt)
        
        try:
            return chain.run(text=text[:4000])  # Limit text length for API
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    def process_documents(self) -> Dict[str, Any]:
        if not self.docs:
            print("No document to process. Load PDFs first.")
            return {}
        
        print("Processing documents...")
        results = {
            "processing_date": datetime.now().isoformat(),
            "total_documents": len(self.docs),
            "files_processed": [],
            "categorized_content": {},
            "summaries": {},
            "task_lists": [],
            "stories": []
        }
        
        # Group docs by source file
        files_content = {}
        for doc in self.docs:
            source_file = doc.metadata.get('source_file', 'unknown')
            if source_file not in files_content:
                files_content[source_file] = []
            files_content[source_file].append(doc.page_content)
        
        # Process each file
        for filename, pages in files_content.items():
            print(f"Processing {filename}...")
            
            # Combine all pages from the files
            full_text = "\n\n".join(pages)
            
            # Categorize content
            categorization = self.categorize_content(full_text)
            content_type = categorization.get('content_type', 'general')
            
            # Generate summary
            summary = self.generate_summary(full_text, content_type)
            
            # Store results
            results["files_processed"].append(filename)
            results["categorized_content"][filename] = categorization
            results["summaries"][filename] = {
                "content_type": content_type,
                "summary": summary,
            }
            
            # Add to specific categories
            if content_type.lower() in ["task", "action", "todo"]:
                task_info = {
                    "file": filename,
                    "tasks": categorization.get('action_items', []),
                    "urgency": categorization.get('urgency_level', 'none'),
                    "summary": summary
                }
                results["task_lists"].append(task_info)
            
            elif content_type.lower() in ["story", "narrative", "fiction"]:
                story_info = {
                    "file": filename,
                    "summary": summary,
                    "characters": categorization.get('key_entities', []),
                    "themes": categorization.get('main_topics', [])
                }
                results["stories"].append(story_info)
        
        return results
    
    def save_results(self, results: Dict[str, Any]):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save complete results as JSON
        json_file = self.output_folder / f"analysis_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Create readable report
        report_file = self.output_folder / f"summary_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# PDF Analysis Report\n\n")
            f.write(f"**Generated:** {results['processing_date']}\n")
            f.write(f"**Files Processed:** {results['total_documents']} docs from {len(results['files_processed'])} files\n\n")
            
            # Task Lists
            if results['task_lists']:
                f.write("## Task Lists\n\n")
                for task_info in results['task_lists']:
                    f.write(f"### {task_info['file']}\n")
                    f.write(f"**Urgency:** {task_info['urgency']}\n\n")
                    if task_info['tasks']:
                        f.write("**Action Items:**\n")
                        for task in task_info['tasks']:
                            f.write(f"- [ ] {task}\n")
                    f.write(f"\n**Summary:**\n{task_info['summary']}\n\n")
            
            # Stories
            if results['stories']:
                f.write("## Stories\n\n")
                for story_info in results['stories']:
                    f.write(f"### {story_info['file']}\n")
                    if story_info['characters']:
                        f.write(f"**Characters:** {', '.join(story_info['characters'])}\n")
                    if story_info['themes']:
                        f.write(f"**Themes:** {', '.join(story_info['themes'])}\n")
                    f.write(f"\n**Summary:**\n{story_info['summary']}\n\n")
            
            # All Summaries
            f.write("## Document Summaries\n\n")
            for filename, summary_info in results['summaries'].items():
                f.write(f"### {filename}\n")
                f.write(f"**Type:** {summary_info['content_type']}\n")
                f.write(f"**Summary:**\n{summary_info['summary']}\n\n")
    
    def run_analysis(self): 
        # Load PDFs
        docs = self.load_pdfs()
        if not docs:
            print("No docs to process. Please add PDF files to the pdf-inputs folder.")
            return
        
        # Create vector store (for future similarity searches)
        self.create_vectorstore()
        
        # Process docs
        results = self.process_documents()
        
        # Save results
        self.save_results(results)
        
        print("\nAnalysis complete!")

def main():
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY environment variable not set.")
        return
    
    # Initialize analyzer
    analyzer = PDFAnalyzer()
    
    # Run analysis
    analyzer.run_analysis()

if __name__ == "__main__":
    main()

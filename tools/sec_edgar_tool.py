"""
SEC EDGAR tool with RAG for 10-K/10-Q analysis.
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from config.settings import settings
from data.fetchers import SECEdgarFetcher


class SECEdgarRAGTool:
    """RAG tool for analyzing SEC 10-K and 10-Q filings."""

    def __init__(self):
        """Initialize SEC EDGAR RAG tool."""
        self.fetcher = SECEdgarFetcher()
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.vector_stores: Dict[str, Chroma] = {}

    def download_filing(self, ticker: str, filing_type: str = "10-K") -> Optional[Path]:
        """
        Download SEC filing for analysis.

        Args:
            ticker: Stock ticker symbol
            filing_type: Type of filing (10-K or 10-Q)

        Returns:
            Path to downloaded filing
        """
        print(f"Downloading {filing_type} for {ticker}...")
        filing_path = self.fetcher.get_filing(ticker, filing_type, limit=1)

        if filing_path and filing_path.exists():
            print(f"Successfully downloaded {filing_type} for {ticker}")
            return filing_path
        else:
            print(f"Failed to download {filing_type} for {ticker}")
            return None

    def load_and_index_filing(self, ticker: str, filing_type: str = "10-K") -> bool:
        """
        Load SEC filing and create vector index.

        Args:
            ticker: Stock ticker symbol
            filing_type: Type of filing (10-K or 10-Q)

        Returns:
            True if successful, False otherwise
        """
        # Download filing if not already cached
        filing_path = self.download_filing(ticker, filing_type)
        if not filing_path:
            return False

        try:
            # Load all text files from the filing directory
            documents = []
            for file_path in filing_path.glob("**/*.txt"):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "ticker": ticker,
                            "filing_type": filing_type,
                            "source": str(file_path)
                        }
                    ))

            if not documents:
                print(f"No documents found in {filing_path}")
                return False

            # Split documents into chunks
            print(f"Splitting {len(documents)} documents into chunks...")
            chunks = self.text_splitter.split_documents(documents)
            print(f"Created {len(chunks)} chunks")

            # Create vector store
            store_key = f"{ticker}_{filing_type}"
            persist_directory = Path(settings.VECTOR_STORE_PATH) / store_key
            persist_directory.mkdir(parents=True, exist_ok=True)

            print(f"Creating vector store for {ticker} {filing_type}...")
            self.vector_stores[store_key] = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=str(persist_directory)
            )

            print(f"Successfully indexed {filing_type} for {ticker}")
            return True

        except Exception as e:
            print(f"Error indexing filing for {ticker}: {e}")
            return False

    def query_filing(
        self,
        ticker: str,
        query: str,
        filing_type: str = "10-K",
        top_k: int = None
    ) -> List[Document]:
        """
        Query the SEC filing using RAG.

        Args:
            ticker: Stock ticker symbol
            query: Natural language query
            filing_type: Type of filing (10-K or 10-Q)
            top_k: Number of top results to return

        Returns:
            List of relevant document chunks
        """
        if top_k is None:
            top_k = settings.RAG_TOP_K

        store_key = f"{ticker}_{filing_type}"

        # Load vector store if not already in memory
        if store_key not in self.vector_stores:
            persist_directory = Path(settings.VECTOR_STORE_PATH) / store_key

            if not persist_directory.exists():
                # Need to index the filing first
                print(f"Vector store not found. Indexing {filing_type} for {ticker}...")
                if not self.load_and_index_filing(ticker, filing_type):
                    return []

            # Load existing vector store
            self.vector_stores[store_key] = Chroma(
                persist_directory=str(persist_directory),
                embedding_function=self.embeddings
            )

        # Perform similarity search
        results = self.vector_stores[store_key].similarity_search(query, k=top_k)
        return results

    def analyze_section(
        self,
        ticker: str,
        section_queries: List[str],
        filing_type: str = "10-K"
    ) -> Dict[str, str]:
        """
        Analyze specific sections of the filing.

        Args:
            ticker: Stock ticker symbol
            section_queries: List of queries for different sections
            filing_type: Type of filing

        Returns:
            Dictionary mapping queries to relevant content
        """
        results = {}

        for query in section_queries:
            print(f"Querying: {query}")
            docs = self.query_filing(ticker, query, filing_type)

            if docs:
                # Combine top results
                combined_content = "\n\n".join([doc.page_content for doc in docs])
                results[query] = combined_content
            else:
                results[query] = "No relevant information found."

        return results


# Function to create tool for AutoGen
def create_sec_rag_function(rag_tool: SECEdgarRAGTool):
    """
    Create a function that can be used as an AutoGen tool.

    Args:
        rag_tool: Instance of SECEdgarRAGTool

    Returns:
        Function that can be registered with AutoGen
    """
    def query_10k(ticker: str, query: str) -> str:
        """
        Query the most recent 10-K filing for a company.

        Args:
            ticker: Stock ticker symbol
            query: Natural language query about the 10-K

        Returns:
            Relevant information from the 10-K filing
        """
        results = rag_tool.query_filing(ticker, query, filing_type="10-K")

        if not results:
            return f"No 10-K information found for {ticker}. The filing may need to be downloaded first."

        # Combine results with source information
        response = f"Information from {ticker} 10-K filing:\n\n"
        for i, doc in enumerate(results, 1):
            response += f"[Result {i}]\n{doc.page_content}\n\n"

        return response

    return query_10k


# Predefined queries for fundamental analysis
FUNDAMENTAL_ANALYSIS_QUERIES = [
    "What is the company's revenue growth and trends?",
    "What is the company's net income and profitability?",
    "What are the company's cash flow from operations?",
    "What is the company's gross margin and operating margin?",
    "What are the main risk factors mentioned in the filing?",
    "What are the company's strategic objectives and future plans?",
    "What is the company's competitive position in the market?",
    "What are the company's key financial metrics and ratios?"
]

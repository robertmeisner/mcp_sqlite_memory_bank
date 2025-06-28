"""
Semantic search functionality for SQLite Memory Bank using sentence-transformers.

This module provides vector embeddings and semantic similarity search capabilities
to enhance the memory bank's knowledge discovery features.

Author: Robert Meisner
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

# Optional imports with graceful fallback
try:
    from sentence_transformers import SentenceTransformer, util

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None  # type: ignore
    util = None  # type: ignore
    logging.warning(
        "sentence-transformers not available. Install with: pip install sentence-transformers"
    )

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None  # type: ignore
    logging.warning("torch not available. Install with: pip install torch")

from .types import ValidationError, DatabaseError


class SemanticSearchEngine:
    """
    Handles semantic search using sentence-transformers.

    Features:
    - Vector embeddings for text content
    - Semantic similarity search
    - Hybrid search combining semantic + keyword matching
    - Caching for performance
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the semantic search engine."""
        self.model_name = model_name
        self._model = None
        self._embedding_cache: Dict[str, Any] = {}

        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ValueError(
                "sentence-transformers is not available. Please install with: pip install sentence-transformers"
            )

    @property
    def model(self) -> Any:
        """Lazy load the sentence transformer model."""
        if self._model is None:
            if not SENTENCE_TRANSFORMERS_AVAILABLE or SentenceTransformer is None:
                raise ValueError("sentence-transformers is not available")
            try:
                self._model = SentenceTransformer(self.model_name)
                logging.info(f"Loaded semantic search model: {self.model_name}")
            except Exception as e:
                raise DatabaseError(f"Failed to load semantic search model {self.model_name}: {e}")
        return self._model

    def get_embedding_dimensions(self) -> Optional[int]:
        """Get the embedding dimension size for the current model."""
        return self.model.get_sentence_embedding_dimension()

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValidationError("Text cannot be empty for embedding generation")

        # Check cache first
        cache_key = f"{self.model_name}:{hash(text)}"
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]

        try:
            # Generate embedding
            embedding = self.model.encode([text], convert_to_tensor=False)[0]
            embedding_list = embedding.tolist()

            # Cache for future use
            self._embedding_cache[cache_key] = embedding_list

            return embedding_list
        except Exception as e:
            raise DatabaseError(f"Failed to generate embedding: {e}")

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Filter out empty texts
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            raise ValidationError("No valid texts provided for embedding generation")

        try:
            embeddings = self.model.encode(
                valid_texts,
                convert_to_tensor=False,
                show_progress_bar=len(valid_texts) > 10,
            )
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            raise DatabaseError(f"Failed to generate batch embeddings: {e}")

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        if not TORCH_AVAILABLE or torch is None:
            # Fallback to numpy implementation
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            similarity = float(np.dot(embedding1, embedding2) / (norm1 * norm2))
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]

        if not SENTENCE_TRANSFORMERS_AVAILABLE or util is None:
            # Fallback to numpy implementation
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            similarity = float(np.dot(embedding1, embedding2) / (norm1 * norm2))
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]

        try:
            # Convert to tensors for efficient computation
            emb1_tensor = torch.tensor(embedding1)
            emb2_tensor = torch.tensor(embedding2)

            # Calculate cosine similarity
            similarity = util.cos_sim(emb1_tensor, emb2_tensor).item()
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
        except Exception as e:
            raise DatabaseError(f"Failed to calculate similarity: {e}")

    def find_similar_embeddings(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        similarity_threshold: float = 0.5,
        top_k: int = 10,
    ) -> List[Tuple[int, float]]:
        """
        Find the most similar embeddings to a query embedding.

        Args:
            query_embedding: Query vector
            candidate_embeddings: List of candidate vectors
            similarity_threshold: Minimum similarity score
            top_k: Maximum number of results

        Returns:
            List of (index, similarity_score) tuples, sorted by similarity descending
        """
        if not candidate_embeddings:
            return []

        # Use efficient torch/sentence-transformers if available
        if (
            TORCH_AVAILABLE
            and torch is not None
            and SENTENCE_TRANSFORMERS_AVAILABLE
            and util is not None
        ):
            try:
                # Convert to tensors
                query_tensor = torch.tensor(query_embedding).unsqueeze(0)
                candidate_tensor = torch.tensor(candidate_embeddings)

                # Calculate similarities
                similarities = util.cos_sim(query_tensor, candidate_tensor)[0]

                # Find matches above threshold
                results = []
                for idx, sim in enumerate(similarities):
                    sim_score = sim.item()
                    if sim_score >= similarity_threshold:
                        results.append((idx, sim_score))

                # Sort by similarity descending and limit to top_k
                results.sort(key=lambda x: x[1], reverse=True)
                return results[:top_k]
            except Exception as e:
                logging.warning(f"Torch similarity search failed, using numpy fallback: {e}")

        # Fallback to numpy implementation
        results = []
        for idx, candidate_emb in enumerate(candidate_embeddings):
            similarity = self.calculate_similarity(query_embedding, candidate_emb)
            if similarity >= similarity_threshold:
                results.append((idx, similarity))

        # Sort by similarity descending and limit to top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def semantic_search(
        self,
        query: str,
        content_data: List[Dict[str, Any]],
        embedding_column: str = "embedding",
        content_columns: Optional[List[str]] = None,
        similarity_threshold: float = 0.5,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search on content data.

        Args:
            query: Natural language search query
            content_data: List of rows with embeddings and content
            embedding_column: Column name containing embeddings
            content_columns: Columns to search in (for highlighting)
            similarity_threshold: Minimum similarity score
            top_k: Maximum number of results

        Returns:
            List of search results with similarity scores
        """
        if not query.strip():
            raise ValidationError("Search query cannot be empty")

        if not content_data:
            return []

        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)

            # Extract embeddings from content data
            candidate_embeddings = []
            valid_indices = []

            for idx, row in enumerate(content_data):
                if embedding_column in row and row[embedding_column]:
                    try:
                        # Parse embedding from JSON string or use directly if already a list
                        embedding = row[embedding_column]
                        if isinstance(embedding, str):
                            embedding = json.loads(embedding)

                        candidate_embeddings.append(embedding)
                        valid_indices.append(idx)
                    except (json.JSONDecodeError, TypeError) as e:
                        logging.warning(f"Invalid embedding data in row {idx}: {e}")
                        continue

            if not candidate_embeddings:
                return []

            # Find similar embeddings
            similar_indices = self.find_similar_embeddings(
                query_embedding, candidate_embeddings, similarity_threshold, top_k
            )

            # Build results
            results = []
            for candidate_idx, similarity_score in similar_indices:
                original_idx = valid_indices[candidate_idx]
                row = content_data[original_idx].copy()

                # Remove embedding data to avoid polluting LLM responses
                if embedding_column in row:
                    del row[embedding_column]

                # Add similarity score
                row["similarity_score"] = round(similarity_score, 3)

                # Add matched content highlighting if specified
                if content_columns:
                    matched_content = []
                    for col in content_columns:
                        if col in row and row[col] and query.lower() in str(row[col]).lower():
                            matched_content.append(f"{col}: {row[col]}")
                    if matched_content:
                        row["matched_content"] = matched_content

                results.append(row)

            return results

        except Exception as e:
            raise DatabaseError(f"Semantic search failed: {e}")

    def hybrid_search(
        self,
        query: str,
        content_data: List[Dict[str, Any]],
        text_columns: Optional[List[str]] = None,
        embedding_column: str = "embedding",
        semantic_weight: float = 0.7,
        text_weight: float = 0.3,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Combine semantic search with keyword matching for better results.

        Args:
            query: Search query
            content_data: Content to search
            text_columns: Columns to perform text search on
            embedding_column: Column containing embeddings
            semantic_weight: Weight for semantic similarity (0-1)
            text_weight: Weight for text matching (0-1)
            top_k: Maximum results

        Returns:
            Ranked search results
        """
        if not content_data:
            return []

        # Normalize weights
        total_weight = semantic_weight + text_weight
        if total_weight > 0:
            semantic_weight /= total_weight
            text_weight /= total_weight

        # Get semantic search results
        semantic_results = self.semantic_search(
            query,
            content_data,
            embedding_column,
            similarity_threshold=0.3,
            top_k=top_k * 2,  # Get more for reranking
        )

        # Add text matching scores
        query_lower = query.lower()
        for result in semantic_results:
            text_score = 0.0

            if text_columns:
                for col in text_columns:
                    if col in result and result[col]:
                        content = str(result[col]).lower()
                        if query_lower in content:
                            # Simple frequency-based text scoring
                            text_score += content.count(query_lower) / len(content.split())

            # Combine scores
            semantic_score = result.get("similarity_score", 0.0)
            combined_score = (semantic_score * semantic_weight) + (text_score * text_weight)
            result["combined_score"] = round(combined_score, 3)
            result["text_score"] = round(text_score, 3)

        # Sort by combined score
        semantic_results.sort(key=lambda x: x.get("combined_score", 0), reverse=True)

        return semantic_results[:top_k]

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._embedding_cache.clear()
        logging.info("Semantic search cache cleared")


# Global instance
_semantic_engine: Optional[SemanticSearchEngine] = None


def get_semantic_engine(model_name: str = "all-MiniLM-L6-v2") -> SemanticSearchEngine:
    """Get or create the global semantic search engine."""
    global _semantic_engine

    try:
        if _semantic_engine is None or _semantic_engine.model_name != model_name:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise ValueError("Sentence transformers not available for semantic search")
            _semantic_engine = SemanticSearchEngine(model_name)

        # Verify the engine is properly initialized
        if not hasattr(_semantic_engine, "hybrid_search"):
            raise ValueError("Semantic engine missing hybrid_search method")

        return _semantic_engine

    except Exception as e:
        raise DatabaseError(f"Failed to initialize semantic engine: {e}")


def is_semantic_search_available() -> bool:
    """Check if semantic search is available."""
    return SENTENCE_TRANSFORMERS_AVAILABLE

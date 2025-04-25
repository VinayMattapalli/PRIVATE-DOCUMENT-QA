# File: app/core/faiss_wrapper.py

import faiss
import numpy as np
import traceback # Optional: for more detailed error logging if needed

# Ensures no self-import or incorrect module-level instantiation occurs here

class FaissIndex:
    def __init__(self, dim: int):
        """Initializes the Faiss index."""
        if not isinstance(dim, int) or dim <= 0:
            raise ValueError(f"Dimension 'dim' must be a positive integer, got {dim}")
        try:
            self.index = faiss.IndexFlatL2(dim)
            self.text_chunks = []
            self._dimension = dim # Store dimension if needed later
            print(f"Initialized FaissIndex with dimension {dim}. Index is_trained: {self.index.is_trained}")
        except Exception as e:
            print(f"Error initializing Faiss Index: {e}")
            print(traceback.format_exc())
            raise # Re-raise the exception after logging

    @property
    def dimension(self):
        """Returns the dimension of the index."""
        return self._dimension

    def add(self, embedding: np.ndarray, chunk: str):
        """Adds a single embedding and its corresponding text chunk."""
        try:
            # Input validation
            if not isinstance(embedding, np.ndarray):
                raise TypeError("Embedding must be a numpy array.")
            if embedding.ndim == 1:
                if embedding.shape[0] != self.dimension:
                    raise ValueError(f"Embedding dimension ({embedding.shape[0]}) does not match index dimension ({self.dimension}).")
                embedding = np.expand_dims(embedding, axis=0) # Expand dims to make it (1, dim)
            elif embedding.ndim == 2:
                 if embedding.shape[0] != 1 or embedding.shape[1] != self.dimension:
                     raise ValueError(f"2D Embedding shape ({embedding.shape}) must be (1, {self.dimension}).")
            else:
                 raise ValueError(f"Embedding must be 1D or 2D (shape (1, dim)), got ndim={embedding.ndim}")

            # Ensure correct data type for FAISS
            if embedding.dtype != np.float32:
                 embedding = embedding.astype(np.float32)

            # Add to FAISS index and store text chunk
            self.index.add(embedding)
            self.text_chunks.append(chunk)
            # Optional: print(f"Added chunk. Index size: {self.index.ntotal}")

        except Exception as e:
            print(f"Error adding embedding/chunk: {e}")
            embedding_info = f"shape: {embedding.shape}, dtype: {embedding.dtype}" if isinstance(embedding, np.ndarray) else "N/A"
            print(f"Embedding info: {embedding_info}")
            print(traceback.format_exc())
            # Decide if you want to re-raise or just log the error
            # raise

    def search(self, query_vector: np.ndarray, top_k=3): # Default k added back
        """Searches the index for the top_k nearest neighbors."""
        try:
            # Check if index is ready/populated before searching
            if not self.is_ready():
                print("Warning: Searching an empty or non-ready index.")
                return [] # Return empty list if nothing to search

            # Input validation for query vector
            if not isinstance(query_vector, np.ndarray):
                 raise TypeError("Query vector must be a numpy array.")
            if query_vector.ndim == 1:
                if query_vector.shape[0] != self.dimension:
                     raise ValueError(f"Query vector dimension ({query_vector.shape[0]}) does not match index dimension ({self.dimension}).")
                query_vector = np.expand_dims(query_vector, axis=0) # Make it (1, dim)
            elif query_vector.ndim == 2:
                 if query_vector.shape[0] != 1 or query_vector.shape[1] != self.dimension:
                      raise ValueError(f"2D Query vector shape ({query_vector.shape}) must be (1, {self.dimension}).")
            else:
                 raise ValueError(f"Query vector must be 1D or 2D (shape (1, dim)), got ndim={query_vector.ndim}")

            if query_vector.dtype != np.float32:
                query_vector = query_vector.astype(np.float32)

            # Adjust top_k if it's larger than the number of items in the index
            actual_k = min(top_k, self.index.ntotal)
            if actual_k <= 0:
                 return []

            # Perform the search
            distances, indices = self.index.search(query_vector, actual_k)

            # Retrieve the corresponding text chunks
            results = [self.text_chunks[i] for i in indices[0] if 0 <= i < len(self.text_chunks)]
            # Optional: print(f"Search found indices: {indices[0]}, Distances: {distances[0]}")
            return results

        except Exception as e:
            print(f"Error during search: {e}")
            query_info = f"shape: {query_vector.shape}, dtype: {query_vector.dtype}" if isinstance(query_vector, np.ndarray) else "N/A"
            print(f"Query vector info: {query_info}, top_k={top_k}")
            print(traceback.format_exc())
            return [] # Return empty list on error

    def reset(self):
        """
        Resets the index, removing all stored vectors and text chunks.
        """
        try:
            current_size = self.index.ntotal
            self.index.reset()
            self.text_chunks = []
            print(f"FaissIndex reset. Removed {current_size} items. Index size is now: {self.index.ntotal}")
        except Exception as e:
            print(f"Error resetting index: {e}")
            print(traceback.format_exc())

    def is_ready(self):
        """
        Checks if the index contains any vectors (i.e., is populated and ready for search).
        """
        try:
            return self.index.ntotal > 0
        except Exception as e:
            print(f"Error checking index readiness: {e}")
            print(traceback.format_exc())
            return False # Assume not ready if check fails

    def __len__(self):
        """Returns the number of items currently in the index."""
        try:
            return self.index.ntotal
        except Exception as e:
            print(f"Error getting index length: {e}")
            print(traceback.format_exc())
            return 0 # Return 0 if error occurs

# --- Example Usage Guard ---
if __name__ == "__main__":
    print("FaissIndex class definition loaded.")
    # Example usage code could go here for direct testing of this file
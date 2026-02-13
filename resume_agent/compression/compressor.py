try:
    from scaledown import ScaleDownCompressor
except ImportError:
    print("WARNING: ScaleDown not found. Compression disabled.")
    ScaleDownCompressor = None

from typing import Optional

class ContextCompressor:
    """Wraps ScaleDown Compressor."""
    
    def __init__(self, api_key: Optional[str] = None):
        if ScaleDownCompressor:
            # We assume api_key is handled by env var or passed here
            # config.py loads SCALEDOWN_API_KEY into env
            self.compressor = ScaleDownCompressor(target_model="gpt-4o", rate="auto")
        else:
            self.compressor = None
            
    def compress(self, context: str, prompt: str) -> str:
        """
        Compresses context using ScaleDown.
        """
        if not self.compressor:
            return context
            
        try:
            result = self.compressor.compress(context=context, prompt=prompt)
            # result might be a CompressedPrompt object, check API
            # created in reading step: result.content
            return result.content
        except Exception as e:
            print(f"Compression failed: {e}")
            return context

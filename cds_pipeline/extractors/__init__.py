from .acroform import AcroFormExtractor
from .native_text import NativeTextExtractor
from .ocr_fallback import OcrFallbackExtractor
from .structured_layout import StructuredLayoutExtractor
from .table import TableExtractor
from .vision_llm import VisionLLMExtractor

EXTRACTOR_REGISTRY = {
    "AcroFormExtractor": AcroFormExtractor,
    "VisionLLMExtractor": VisionLLMExtractor,
    "TableExtractor": TableExtractor,
    "NativeTextExtractor": NativeTextExtractor,
    "StructuredLayoutExtractor": StructuredLayoutExtractor,
    "OcrFallbackExtractor": OcrFallbackExtractor,
}

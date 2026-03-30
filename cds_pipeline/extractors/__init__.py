from .acroform import AcroFormExtractor
from .native_text import NativeTextExtractor
from .ocr_fallback import OcrFallbackExtractor
from .structured_layout import StructuredLayoutExtractor

EXTRACTOR_REGISTRY = {
    "AcroFormExtractor": AcroFormExtractor,
    "NativeTextExtractor": NativeTextExtractor,
    "StructuredLayoutExtractor": StructuredLayoutExtractor,
    "OcrFallbackExtractor": OcrFallbackExtractor,
}

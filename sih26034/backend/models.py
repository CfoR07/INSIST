from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import date, datetime

class BoundingBox(BaseModel):
    ymin: float = Field(..., description="Top coordinate (0.0 to 1.0 or pixel y)")
    xmin: float = Field(..., description="Left coordinate (0.0 to 1.0 or pixel x)")
    ymax: float = Field(..., description="Bottom coordinate")
    xmax: float = Field(..., description="Right coordinate")

class OCRToken(BaseModel):
    text: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    bounding_box: Optional[List[float]] = None
    source_view: Optional[str] = None

class RawOCRResult(BaseModel):
    image_id: str
    raw_text: str
    tokens: List[OCRToken] = Field(default_factory=list)
    mean_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    ocr_engine: str = "WinOCR/PaddleOCR"

class DeclarationField(BaseModel):
    raw_value: Optional[str] = Field(default=None, description="Exact OCR snippet as detected on packaging")
    normalized_value: Optional[Any] = Field(default=None, description="Cleaned, typed value for deterministic validation")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_ocr_id: Optional[str] = None
    bounding_box: Optional[List[float]] = None
    source_view_type: Optional[str] = None

class QuantityDeclaration(DeclarationField):
    normalized_value: Optional[float] = Field(default=None, description="Numeric magnitude in standard unit (e.g. 500.0)")
    unit: Optional[str] = Field(default=None, description="Standard metric unit: g, kg, ml, l, m, cm, mm, n, units, pcs")

class PriceDeclaration(DeclarationField):
    normalized_value: Optional[float] = Field(default=None, description="Numeric price in INR (e.g. 50.00)")
    currency: str = "INR"
    tax_inclusive: bool = Field(default=True, description="Whether inclusive of all taxes is declared")

class UnitSalePriceDeclaration(DeclarationField):
    normalized_value: Optional[float] = Field(default=None, description="Numeric rate per standard unit (e.g. 0.10)")
    unit: Optional[str] = Field(default=None, description="Standard reference unit: Rs/g, Rs/kg, Rs/ml, Rs/l, Rs/unit")

class DateDeclaration(DeclarationField):
    normalized_value: Optional[str] = Field(default=None, description="ISO Date string or MM/YYYY")

class ConsumerCareDeclaration(DeclarationField):
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ProductSchema(BaseModel):
    product_name: Optional[str] = Field(default=None, description="Commercial / generic name of the pre-packed commodity")
    brand: Optional[str] = Field(default=None, description="Brand name or trademark")
    category_id: str = Field(default="CAT-ALL", description="Target category ID mapped from controlled taxonomy")
    category_name: Optional[str] = None
    category_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Statutory Declarations
    manufacturer_name: Optional[str] = None
    manufacturer_address: Optional[str] = None
    packer_name: Optional[str] = None
    packer_address: Optional[str] = None
    importer_name: Optional[str] = None
    importer_address: Optional[str] = None
    country_of_origin: Optional[str] = None
    
    net_quantity: QuantityDeclaration = Field(default_factory=QuantityDeclaration)
    mrp: PriceDeclaration = Field(default_factory=PriceDeclaration)
    unit_sale_price: UnitSalePriceDeclaration = Field(default_factory=UnitSalePriceDeclaration)
    manufacture_date: DateDeclaration = Field(default_factory=DateDeclaration)
    expiry_date: DateDeclaration = Field(default_factory=DateDeclaration)
    batch_number: Optional[str] = None
    consumer_care: ConsumerCareDeclaration = Field(default_factory=ConsumerCareDeclaration)
    veg_nonveg_status: str = Field(default="NONE", description="VEG, NON_VEG, or NONE")
    
    extraction_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    requires_human_review: bool = Field(default=False, description="Flag set if any critical field or category is uncertain")

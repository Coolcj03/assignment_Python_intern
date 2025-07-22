# receipt_processor.py
import os
import re
import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import pandas as pd
import numpy as np
from dataclasses import dataclass
import json
import io

from database import Database
from algorithms import Sorting, Searching, Aggregation

# Set up basic logging - only want to see the important stuff
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import OCR stuff - if it's not installed, we'll handle it gracefully
try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("OCR libraries not found - image text extraction won't work")

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("PDF library not found - PDF processing won't work")

# Some basic limits to prevent issues
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB should be more than enough
ALLOWED_TYPES = {'.jpg', '.jpeg', '.png', '.pdf', '.txt'}

class ReceiptProcessingError(Exception):
    """When something goes wrong with receipt processing"""
    pass

@dataclass
class Receipt:
    """Simple receipt data structure"""
    filename: str
    vendor: str
    date: str
    amount: float
    category: str = "Other"
    text: str = ""
    upload_date: str = ""
    file_hash: str = ""
    currency: str = "USD"      # Added for multi-currency support
    language: str = "en"       # Added for multi-language support
    id: Optional[int] = None
    
    def __post_init__(self):
        # Make sure we have the basics
        if not self.filename:
            raise ValueError("Need a filename")
        if not self.vendor:
            raise ValueError("Need a vendor name")
        if not isinstance(self.amount, (int, float)) or self.amount < 0:
            raise ValueError("Amount needs to be a positive number")
        
        # Auto-set upload date if not provided
        if not self.upload_date:
            self.upload_date = datetime.now().isoformat()
        
        # Validate date format
        try:
            datetime.strptime(self.date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be YYYY-MM-DD format")

class FileHandler:
    """Handles file operations and text extraction"""
    
    def __init__(self):
        self.supported_types = {
            'image': ['.jpg', '.jpeg', '.png', '.bmp'],
            'pdf': ['.pdf'],
            'text': ['.txt']
        }
    
    def check_file(self, file_data, filename):
        """Basic file validation"""
        if not file_data:
            raise ReceiptProcessingError("File is empty")
        
        if len(file_data) > MAX_FILE_SIZE:
            raise ReceiptProcessingError(f"File too big ({len(file_data)} bytes)")
        
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_TYPES:
            raise ReceiptProcessingError(f"File type {ext} not supported")
    
    def get_file_type(self, filename):
        """Figure out what kind of file this is"""
        ext = Path(filename).suffix.lower()
        for file_type, extensions in self.supported_types.items():
            if ext in extensions:
                return file_type
        return 'unknown'
    
    def extract_text(self, file_data, filename):
        """Extract text from different file types"""
        self.check_file(file_data, filename)
        file_type = self.get_file_type(filename)
        try:
            if file_type == 'image':
                return self._extract_from_image(file_data)
            elif file_type == 'pdf':
                return self._extract_from_pdf(file_data)
            elif file_type == 'text':
                return self._extract_from_text(file_data)
            else:
                return f"Can't extract text from {filename}"
        except Exception as e:
            logger.warning(f"Text extraction failed for {filename}: {e}")
            return f"Text extraction failed: {str(e)}"
    
    def _extract_from_image(self, file_data):
        """Get text from images using OCR"""
        if not HAS_OCR:
            return "OCR not available - need to install pytesseract and PIL"
        
        try:
            img = Image.open(io.BytesIO(file_data))
            text = pytesseract.image_to_string(img)
            return text.strip() if text else "No text found in image"
        except Exception as e:
            return f"OCR failed: {str(e)}"
    
    def _extract_from_pdf(self, file_data):
        """Extract text from PDF files"""
        if not HAS_PDF:
            return "PDF processing not available - need PyPDF2"
        
        try:
            pdf = PyPDF2.PdfReader(io.BytesIO(file_data))
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text.strip() if text.strip() else "No text in PDF"
        except Exception as e:
            return f"PDF extraction failed: {str(e)}"

    def _extract_from_text(self, file_data):
        """Handle text files with encoding issues"""
        # Try common encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                return file_data.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        # Last resort - replace bad characters
        return file_data.decode('utf-8', errors='replace')
    
    def get_file_hash(self, file_data):
        """Generate hash for duplicate detection"""
        return hashlib.sha256(file_data).hexdigest()

class ReceiptParser:
    """Parses receipt text to extract useful info"""
    
    def __init__(self):
        # Common store patterns I've noticed
        self.vendor_patterns = {
            'walmart': r'walmart|supercenter',
            'target': r'target',
            'amazon': r'amazon',
            'costco': r'costco',
            'starbucks': r'starbucks',
            'mcdonalds': r'mcdonald\'?s',
            'shell': r'shell',
            'exxon': r'exxon',
            'kroger': r'kroger',
            'home depot': r'home\s*depot',
        }
        
        # Category mapping based on stores
        self.categories = {
            'walmart': 'Groceries',
            'target': 'Shopping',
            'amazon': 'Online',
            'costco': 'Wholesale',
            'starbucks': 'Food',
            'mcdonalds': 'Food',
            'shell': 'Gas',
            'exxon': 'Gas',
            'kroger': 'Groceries',
            'home depot': 'Home Improvement',
        }
    
    def parse(self, text, filename):
        """Parse receipt text and extract key info"""
        if not text or not text.strip():
            return self._get_defaults(filename)
        
        text_clean = text.lower().strip()
        
        vendor = self._find_vendor(text_clean, filename)
        amount = self._find_amount(text_clean)
        date = self._find_date(text_clean)
        category = self.categories.get(vendor.lower(), 'Other')
        
        return {
            'vendor': vendor,
            'amount': amount,
            'date': date,
            'category': category
        }
    
    def _get_defaults(self, filename):
        """Fallback values when parsing fails"""
        return {
            'vendor': filename.split('.')[0][:30],
            'amount': 0.0,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'category': 'Other'
        }
    
    def _find_vendor(self, text, filename):
        """Try to identify the vendor from text"""
        for vendor, pattern in self.vendor_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return vendor.title()
        
        # If no pattern matches, use first line or filename
        lines = text.strip().split('\n')
        if lines and lines[0].strip():
            return lines[0][:30].strip().title()
        
        return filename.split('.')[0][:30]
    
    def _find_amount(self, text):
        """Extract the total amount"""
        # Common amount patterns I've seen
        patterns = [
            r'total[:\s]*\$?(\d+\.?\d*)',
            r'amount[:\s]*\$?(\d+\.?\d*)',
            r'\$(\d+\.?\d*)',
            r'(\d+\.\d{2})\s*(?:total|due)',
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amt = float(match)
                    if 0 < amt < 10000:  # reasonable range
                        amounts.append(amt)
                except ValueError:
                    continue
        
        return max(amounts) if amounts else 0.0
    
    def _find_date(self, text):
        """Extract the receipt date"""
        patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # 2023-12-25
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # 12/25/2023 or 12-25-23
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                parsed_date = self._parse_date(match)
                if parsed_date:
                    return parsed_date.strftime('%Y-%m-%d')
        # Default to today
        return datetime.now().strftime('%Y-%m-%d')
    
    def _parse_date(self, date_str):
        """Try different date formats"""
        formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', 
            '%m/%d/%y', '%m-%d-%y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

class ReceiptProcessor:
    """Main class that ties everything together"""
    
    def __init__(self, db_file="my_receipts.db"):
        self.db = Database(db_file)
        self.file_handler = FileHandler()
        self.parser = ReceiptParser()
        # Initialize all algorithm classes
        self.sorter = Sorting()
        self.searcher = Searching()
        self.aggregator = Aggregation()
    
    def process_receipt(self, file_data, filename):
        """Process a receipt file from start to finish"""
        try:
            # Extract text from the file
            text = self.file_handler.extract_text(file_data, filename)
            
            # Parse the extracted text
            parsed = self.parser.parse(text, filename)
            
            # Create receipt object
            receipt = Receipt(
                filename=filename,
                vendor=parsed['vendor'],
                date=parsed['date'],
                amount=parsed['amount'],
                category=parsed['category'],
                text=text,
                file_hash=self.file_handler.get_file_hash(file_data)
            )
            
            # Save to database
            receipt_id = self.db.save_receipt(receipt)
            
            return {
                'success': True,
                'receipt_id': receipt_id,
                'extracted_data': {
                    'vendor': receipt.vendor,
                    'amount': receipt.amount,
                    'date': receipt.date,
                    'category': receipt.category,
                    'filename': receipt.filename,
                    'upload_date': receipt.upload_date,
                    # Add currency and language if present
                    'currency': getattr(receipt, 'currency', None),
                    'language': getattr(receipt, 'language', None)
                }
            }
            
        except Exception as e:
            logger.error(f"Processing failed for {filename}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_receipts(self, query, limit=50):
        """Search receipts using keyword search algorithm"""
        try:
            all_receipts = self.db.get_receipts(limit=1000)  # Get more for comprehensive search
            
            # Define which fields to search in
            search_fields = ['vendor', 'category', 'text', 'filename']
            
            # Use the keyword search algorithm
            results = self.searcher.keyword_search(all_receipts, query, search_fields)
            
            return results[:limit]  # Return top results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_spending_analytics(self):
        """Get advanced spending analytics using aggregation algorithms"""
        try:
            all_receipts = self.db.get_receipts(limit=1000)
            
            if not all_receipts:
                return {'error': 'No receipts found'}
            
            # Basic statistics using aggregation methods
            amounts = [receipt['amount'] for receipt in all_receipts if receipt['amount']]
            median_spending = self.aggregator.calculate_median(amounts)
            
            categories = [receipt['category'] for receipt in all_receipts]
            most_common_category = self.aggregator.calculate_mode(categories)
            
            # Group and aggregate by category
            category_aggregations = self.aggregator.group_and_aggregate(
                all_receipts, 
                'category', 
                {'amount': ['sum', 'avg', 'count']}
            )
            
            # Group and aggregate by vendor
            vendor_aggregations = self.aggregator.group_and_aggregate(
                all_receipts,
                'vendor',
                {'amount': ['sum', 'avg', 'count']}
            )
            
            # Time series aggregation by month
            monthly_spending = self.aggregator.time_series_aggregation(
                all_receipts, 
                'date', 
                'amount', 
                'M'
            )
            
            return {
                'total_receipts': len(all_receipts),
                'total_spending': sum(amounts),
                'average_spending': sum(amounts) / len(amounts) if amounts else 0,
                'median_spending': median_spending,
                'most_common_category': most_common_category,
                'category_breakdown': category_aggregations,
                'vendor_breakdown': vendor_aggregations,
                'monthly_spending': monthly_spending
            }
            
        except Exception as e:
            logger.error(f"Analytics failed: {e}")
            return {'error': 'Could not generate analytics'}
    
    def get_dashboard_data(self):
        """Get data for dashboard display"""
        try:
            summary = self.db.get_spending_summary()
            recent_receipts = self.db.get_receipts(10)
            all_receipts = self.db.get_receipts(limit=500) # Get more for sorting
            # Aggregate vendor totals from all receipts
            vendor_totals = {}
            for receipt in all_receipts:
                vendor = receipt['vendor']
                amount = receipt['amount']
                vendor_totals[vendor] = vendor_totals.get(vendor, 0) + amount
            # Prepare for sorting
            vendor_list = [{'vendor': v, 'total_spent': a} for v, a in vendor_totals.items()]
            # Use custom quicksort to get top vendors
            top_vendors = self.sorter.quicksort(vendor_list, 'total_spent', ascending=False)[:5]
            return {
                'summary': summary,
                'recent_receipts': recent_receipts,
                'top_vendors': top_vendors
            }
        except Exception as e:
            logger.error(f"Dashboard data failed: {e}")
            return {'error': 'Could not load dashboard data'}
    
    def get_sorted_receipts(self, sort_by='date', ascending=True, limit=100):
        """Get receipts sorted by specified field using custom sort algorithm"""
        try:
            receipts = self.db.get_receipts(limit=limit)
            if not receipts:
                return []
            # Use the quicksort algorithm from algorithms.py
            sorted_receipts = self.sorter.quicksort(receipts, sort_by, ascending)
            return sorted_receipts
        except Exception as e:
            logger.error(f"Sorting failed: {e}")
            return []
    
    def get_category_insights(self):
        """Get insights about spending categories using aggregation"""
        try:
            all_receipts = self.db.get_receipts(limit=1000)
            if not all_receipts:
                return {'error': 'No receipts found'}
            # Group by category and get comprehensive stats
            category_stats = self.aggregator.group_and_aggregate(
                all_receipts,
                'category',
                {'amount': ['sum', 'avg', 'count'], 'id': ['count']}
            )
            # Sort categories by total spending
            category_list = []
            for category, stats in category_stats.items():
                category_list.append({
                    'category': category,
                    'total_spent': stats.get('amount_sum', 0),
                    'average_amount': stats.get('amount_avg', 0),
                    'transaction_count': stats.get('amount_count', 0)
                })
            # Use quicksort to sort by total spending
            sorted_categories = self.sorter.quicksort(category_list, 'total_spent', ascending=False)
            return {
                'category_insights': sorted_categories,
                'total_categories': len(sorted_categories)
            }
        except Exception as e:
            logger.error(f"Category insights failed: {e}")
            return {'error': 'Could not generate category insights'}
    
    def get_vendor_insights(self):
        """Get insights about vendors using aggregation and sorting"""
        try:
            all_receipts = self.db.get_receipts(limit=1000)
            if not all_receipts:
                return {'error': 'No receipts found'}
            # Group by vendor and get comprehensive stats
            vendor_stats = self.aggregator.group_and_aggregate(
                all_receipts,
                'vendor',
                {'amount': ['sum', 'avg', 'count']}
            )
            # Convert to list for sorting
            vendor_list = []
            for vendor, stats in vendor_stats.items():
                vendor_list.append({
                    'vendor': vendor,
                    'total_spent': stats.get('amount_sum', 0),
                    'average_amount': stats.get('amount_avg', 0),
                    'visit_count': stats.get('amount_count', 0)
                })
            # Sort by total spending using quicksort
            sorted_vendors = self.sorter.quicksort(vendor_list, 'total_spent', ascending=False)
            return {
                'vendor_insights': sorted_vendors,
                'total_vendors': len(sorted_vendors)
            }
        except Exception as e:
            logger.error(f"Vendor insights failed: {e}")
            return {'error': 'Could not generate vendor insights'}

    def get_status(self):
        """Return a simple status string for the analytics engine."""
        return "Online ✅"

    def get_performance_metrics(self):
        """Return mock performance metrics for the analytics engine."""
        return {
            'Accuracy': '94.2%',
            'Processing Speed': '1.2s/receipt',
            'Confidence Score': '96.8%'
        }

from typing import Dict, List, Any, Optional
from supabase import create_client, Client
import os
import re
import json
from datetime import datetime, timedelta
import asyncio

class RealEstateTools:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )
    
    async def extract_search_criteria(self, user_input: str) -> Dict[str, Any]:
        """Extract property search criteria from user input"""
        criteria = {}
        
        # Extract price range
        price_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:k|K)?)\s*(?:to|-)\s*\$?(\d{1,3}(?:,\d{3})*(?:k|K)?)',
            r'under\s*\$?(\d{1,3}(?:,\d{3})*(?:k|K)?)',
            r'up\s*to\s*\$?(\d{1,3}(?:,\d{3})*(?:k|K)?)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:  # Range
                    criteria['price_min'] = self._parse_price(match.group(1))
                    criteria['price_max'] = self._parse_price(match.group(2))
                else:  # Single value (max)
                    criteria['price_max'] = self._parse_price(match.group(1))
                break
        
        # Extract bedrooms
        bedroom_match = re.search(r'(\d+)\s*(?:bed|bedroom)', user_input, re.IGNORECASE)
        if bedroom_match:
            criteria['bedrooms'] = int(bedroom_match.group(1))
        
        # Extract location
        location_patterns = [
            r'in\s+([A-Za-z\s]+?)(?:\s|$|,)',
            r'near\s+([A-Za-z\s]+?)(?:\s|$|,)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if len(location) > 2:
                    criteria['location'] = location
                break
        
        return criteria
    
    def _parse_price(self, price_str: str) -> int:
        """Parse price string to integer"""
        price_str = price_str.replace(',', '').replace('$', '')
        if price_str.lower().endswith('k'):
            return int(float(price_str[:-1]) * 1000)
        return int(price_str)
    
    async def search_properties(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for properties (mock implementation)"""
        mock_properties = [
            {
                "id": "prop_001",
                "address": "123 Oak Street, Downtown",
                "price": 450000,
                "bedrooms": 3,
                "bathrooms": 2.5,
                "property_type": "house",
                "description": "Beautiful single-family home"
            },
            {
                "id": "prop_002", 
                "address": "456 Pine Avenue, Midtown",
                "price": 320000,
                "bedrooms": 2,
                "bathrooms": 2,
                "property_type": "condo",
                "description": "Modern condo with city views"
            }
        ]
        
        return mock_properties[:3]
    
    async def extract_qualification_info(self, user_input: str) -> Dict[str, Any]:
        """Extract lead qualification information"""
        qualification_data = {}
        
        # Extract budget
        price_match = re.search(r'\$?(\d{1,3}(?:,\d{3})*(?:k|K)?)', user_input)
        if price_match and any(word in user_input.lower() for word in ['budget', 'afford']):
            qualification_data['budget'] = self._parse_price(price_match.group(1))
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_input)
        if email_match:
            qualification_data['email'] = email_match.group()
        
        # Extract phone
        phone_match = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', user_input)
        if phone_match:
            qualification_data['phone'] = phone_match.group()
        
        return qualification_data
    
    async def get_missing_qualification_fields(self, lead_info: Dict[str, Any]) -> List[str]:
        """Get missing qualification fields"""
        required_fields = ['budget', 'timeline', 'name', 'email']
        return [field for field in required_fields if field not in lead_info]
    
    async def extract_scheduling_info(self, user_input: str) -> Dict[str, Any]:
        """Extract scheduling information"""
        scheduling_info = {}
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            if day in user_input.lower():
                scheduling_info['preferred_day'] = day
                break
        
        return scheduling_info
    
    async def get_available_slots(self) -> List[Dict[str, Any]]:
        """Get available appointment slots"""
        base_date = datetime.now() + timedelta(days=1)
        slots = []
        
        for i in range(5):
            date = base_date + timedelta(days=i)
            slots.append({
                'date': date.strftime('%Y-%m-%d'),
                'time': '10:00 AM',
                'available': True
            })
        
        return slots
    
    async def classify_info_request(self, user_input: str) -> str:
        """Classify information request type"""
        if any(word in user_input.lower() for word in ['market', 'prices', 'trends']):
            return 'market'
        elif any(word in user_input.lower() for word in ['neighborhood', 'area', 'schools']):
            return 'neighborhood'
        else:
            return 'general'
    
    async def get_market_info(self, info_type: str) -> Dict[str, Any]:
        """Get market information"""
        return {
            'market': {'average_price': '$425,000', 'trend': '+5.2% YoY'},
            'neighborhood': {'school_rating': '8/10', 'safety': 'Above average'},
            'general': {'info': 'General real estate information'}
        }.get(info_type, {'info': 'Information available'})
    
    async def analyze_escalation_need(self, user_input: str) -> str:
        """Analyze escalation need"""
        if any(word in user_input.lower() for word in ['complaint', 'problem', 'issue']):
            return 'complaint'
        return 'general_inquiry'
    
    async def determine_priority(self, escalation_reason: str) -> str:
        """Determine escalation priority"""
        return {'complaint': 'high', 'legal': 'urgent'}.get(escalation_reason, 'low')
    
    async def save_lead_data(self, lead_info: Dict[str, Any]) -> None:
        """Save lead data to Supabase"""
        try:
            lead_data = {k: v for k, v in lead_info.items() if v is not None}
            if lead_data:
                self.supabase.table('leads').insert(lead_data).execute()
        except Exception as e:
            print(f"Error saving lead: {e}") 
import re
import json
import os
from django.conf import settings
from collections import defaultdict
import numpy as np
from difflib import SequenceMatcher
from .models import Category

def load_transaction_dataset():
    """Load the transaction dataset from JSON file"""
    dataset_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'transaction_dataset.json')
    try:
        with open(dataset_path, 'r') as f:
            return json.load(f)['transactions']
    except:
        return []

def preprocess_text(text):
    """Preprocess text for better categorization"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def get_category_suggestions(description):
    """Get category suggestions with confidence scores"""
    if not description:
        return [('Other', 1.0)]
    
    # Create a new categorizer instance
    categorizer = TransactionCategorizer()
    
    # Get category scores
    suggestions = categorizer.get_category_scores(description)
    
    # If no suggestions found, return Other category
    if not suggestions:
        return [('Other', 1.0)]
    
    # Return top 3 suggestions
    return suggestions[:3]

def categorize_transaction(description):
    """Categorize a transaction based on its description"""
    suggestions = get_category_suggestions(description)
    return suggestions[0][0]  # Return the highest scoring category

def get_similar_transactions(description, k=3):
    """Find similar transactions from the dataset"""
    if not description:
        return []
    
    # Load dataset
    dataset_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'transaction_dataset.json')
    try:
        with open(dataset_path, 'r') as f:
            data = json.load(f)
    except:
        return []
    
    # Get all valid categories from the database
    valid_categories = {cat.name.lower(): cat.name for cat in Category.objects.all()}
    
    # Calculate similarity scores
    similarities = []
    for transaction in data['transactions']:
        # Only include transactions with valid categories
        if transaction['category'].lower() in valid_categories:
            score = SequenceMatcher(None, 
                                  preprocess_text(description), 
                                  preprocess_text(transaction['description'])).ratio()
            similarities.append((transaction, score))
    
    # Sort by similarity score
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k similar transactions with valid categories
    return [(t['description'], valid_categories[t['category'].lower()], s) 
            for t, s in similarities[:k]]

# Expanded category keywords with common variations and related terms
CATEGORY_KEYWORDS = {
    'Food & Dining': [
        'restaurant', 'cafe', 'coffee', 'food', 'dining', 'meal', 'lunch', 'dinner', 'breakfast', 'snack',
        'grocery', 'supermarket', 'market', 'bakery', 'butcher', 'deli', 'fast food', 'takeout', 'delivery',
        'pizza', 'burger', 'sandwich', 'salad', 'sushi', 'chinese', 'italian', 'mexican', 'indian', 'thai',
        'starbucks', 'mcdonalds', 'subway', 'kfc', 'dominos', 'grubhub', 'doordash', 'ubereats', 'food delivery',
        'grocery store', 'whole foods', 'trader joes', 'costco', 'walmart', 'target', 'aldi', 'lidl'
    ],
    'Transportation': [
        'uber', 'lyft', 'taxi', 'bus', 'train', 'subway', 'metro', 'transport', 'fuel', 'gas', 'petrol',
        'parking', 'car', 'vehicle', 'auto', 'automotive', 'maintenance', 'repair', 'service', 'oil change',
        'tire', 'brake', 'transit', 'commute', 'travel', 'trip', 'ride', 'cab', 'shuttle', 'ferry',
        'airport', 'terminal', 'station', 'toll', 'fare', 'ticket', 'pass', 'subscription', 'membership'
    ],
    'Shopping': [
        'amazon', 'walmart', 'target', 'store', 'shop', 'mall', 'retail', 'clothing', 'fashion', 'apparel',
        'department store', 'boutique', 'outlet', 'discount', 'sale', 'clearance', 'online shopping',
        'electronics', 'gadget', 'device', 'computer', 'phone', 'laptop', 'tablet', 'accessory',
        'home goods', 'furniture', 'decor', 'kitchen', 'bath', 'bedding', 'linen', 'household',
        'beauty', 'cosmetic', 'makeup', 'skincare', 'haircare', 'personal care', 'toiletries',
        'bookstore', 'music', 'video', 'game', 'toy', 'hobby', 'craft', 'art', 'supply'
    ],
    'Entertainment': [
        'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'youtube', 'music', 'video',
        'subscription', 'membership', 'event', 'festival', 'exhibition', 'museum', 'gallery',
        'theater', 'play', 'musical', 'opera', 'ballet', 'dance', 'performance', 'live',
        'sports', 'game', 'match', 'tournament', 'league', 'ticket', 'season pass'
    ],
    'Bills & Utilities': [
        'electricity', 'water', 'gas', 'internet', 'phone', 'mobile', 'bill', 'utility', 'rent',
        'mortgage', 'payment', 'subscription', 'service', 'provider', 'company', 'vendor',
        'cable', 'tv', 'satellite', 'streaming', 'wifi', 'broadband', 'data', 'plan',
        'insurance', 'premium', 'coverage', 'policy', 'claim', 'deductible', 'copay',
        'tax', 'fee', 'charge', 'due', 'payment', 'installment', 'loan', 'credit'
    ],
    'Health & Fitness': [
        'gym', 'fitness', 'health', 'medical', 'doctor', 'pharmacy', 'medicine', 'dental', 'hospital',
        'clinic', 'practice', 'physician', 'specialist', 'therapist', 'treatment', 'therapy',
        'wellness', 'nutrition', 'diet', 'supplement', 'vitamin', 'protein', 'workout',
        'exercise', 'training', 'coach', 'trainer', 'class', 'yoga', 'pilates', 'crossfit',
        'equipment', 'gear', 'apparel', 'shoes', 'accessory', 'membership', 'subscription'
    ],
    'Travel': [
        'hotel', 'flight', 'airline', 'vacation', 'trip', 'travel', 'booking', 'reservation',
        'accommodation', 'lodging', 'resort', 'motel', 'hostel', 'airbnb', 'rental',
        'transportation', 'transfer', 'shuttle', 'car rental', 'vehicle', 'cruise', 'tour',
        'package', 'deal', 'discount', 'promotion', 'offer', 'booking', 'reservation',
        'ticket', 'pass', 'visa', 'insurance', 'protection', 'assistance', 'service'
    ],
    'Education': [
        'school', 'college', 'university', 'course', 'book', 'textbook', 'tuition', 'education',
        'learning', 'training', 'workshop', 'seminar', 'conference', 'lecture', 'class',
        'program', 'degree', 'certificate', 'diploma', 'qualification', 'accreditation',
        'material', 'supply', 'equipment', 'tool', 'resource', 'software', 'subscription',
        'membership', 'fee', 'payment', 'scholarship', 'grant', 'loan', 'financial aid'
    ],
    'Personal Care': [
        'salon', 'spa', 'beauty', 'haircut', 'cosmetic', 'personal care', 'grooming',
        'hair', 'nail', 'skin', 'facial', 'massage', 'treatment', 'therapy',
        'product', 'item', 'supply', 'tool', 'equipment', 'accessory',
        'service', 'appointment', 'booking', 'reservation', 'visit',
        'professional', 'specialist', 'therapist', 'stylist', 'technician'
    ],
    'Other': []  # Default category
}

class TransactionCategorizer:
    def __init__(self):
        self.category_patterns = defaultdict(list)
        self.category_weights = defaultdict(float)
        self.learned_patterns = defaultdict(list)
        self.initialize_patterns()
        self.load_learned_patterns()
        
    def initialize_patterns(self):
        """Initialize patterns for each category"""
        # Food & Dining patterns
        self.add_patterns('Food & Dining', [
            (r'(restaurant|cafe|coffee|food|dining|meal)', 1.0),
            (r'(grocery|supermarket|market|bakery|butcher)', 0.9),
            (r'(pizza|burger|sandwich|salad|sushi)', 0.8),
            (r'(starbucks|mcdonalds|subway|kfc|dominos)', 0.7),
            (r'(grubhub|doordash|ubereats|food delivery)', 0.7),
            (r'(whole foods|trader joes|costco|walmart|target)', 0.8)
        ])
        
        # Transportation patterns
        self.add_patterns('Transportation', [
            (r'(uber|lyft|taxi|bus|train|subway)', 1.0),
            (r'(transport|fuel|gas|petrol|parking)', 0.9),
            (r'(car|vehicle|auto|automotive|maintenance)', 0.8),
            (r'(tire|brake|transit|commute|travel)', 0.7),
            (r'(airport|terminal|station|toll|fare)', 0.7),
            (r'(ticket|pass|subscription|membership)', 0.8)
        ])
        
        # Shopping patterns
        self.add_patterns('Shopping', [
            (r'(amazon|walmart|target|store|shop|mall)', 1.0),
            (r'(retail|clothing|fashion|apparel|department)', 0.9),
            (r'(electronics|gadget|device|computer|phone)', 0.8),
            (r'(home goods|furniture|decor|kitchen|bath)', 0.7),
            (r'(beauty|cosmetic|makeup|skincare|haircare)', 0.7),
            (r'(bookstore|music|video|game|toy|hobby)', 0.8)
        ])
        
        # Entertainment patterns
        self.add_patterns('Entertainment', [
            (r'(netflix|spotify|hulu|disney|amazon prime)', 1.0),
            (r'(youtube|music|video|subscription|membership)', 0.9),
            (r'(event|festival|exhibition|museum|gallery)', 0.8),
            (r'(theater|play|musical|opera|ballet|dance)', 0.7),
            (r'(performance|live|sports|game|match)', 0.7),
            (r'(tournament|league|ticket|season pass)', 0.8)
        ])
        
        # Bills & Utilities patterns
        self.add_patterns('Bills & Utilities', [
            (r'(electricity|water|gas|internet|phone|mobile)', 1.0),
            (r'(bill|utility|rent|mortgage|payment)', 0.9),
            (r'(subscription|service|provider|company|vendor)', 0.8),
            (r'(cable|tv|satellite|streaming|wifi|broadband)', 0.7),
            (r'(insurance|premium|coverage|policy|claim)', 0.7),
            (r'(tax|fee|charge|due|payment|installment)', 0.8)
        ])
        
        # Health & Fitness patterns
        self.add_patterns('Health & Fitness', [
            (r'(gym|fitness|health|medical|doctor|pharmacy)', 1.0),
            (r'(medicine|dental|hospital|clinic|practice)', 0.9),
            (r'(physician|specialist|therapist|treatment|therapy)', 0.8),
            (r'(wellness|nutrition|diet|supplement|vitamin)', 0.7),
            (r'(protein|workout|exercise|training|coach)', 0.7),
            (r'(trainer|class|yoga|pilates|crossfit)', 0.8)
        ])
        
        # Travel patterns
        self.add_patterns('Travel', [
            (r'(hotel|flight|airline|vacation|trip|travel)', 1.0),
            (r'(booking|reservation|accommodation|lodging|resort)', 0.9),
            (r'(motel|hostel|airbnb|rental|transportation)', 0.8),
            (r'(transfer|shuttle|car rental|vehicle|cruise)', 0.7),
            (r'(tour|package|deal|discount|promotion)', 0.7),
            (r'(offer|booking|reservation|ticket|pass)', 0.8)
        ])
        
        # Education patterns
        self.add_patterns('Education', [
            (r'(school|college|university|course|book|textbook)', 1.0),
            (r'(tuition|education|learning|training|workshop)', 0.9),
            (r'(seminar|conference|lecture|class|program)', 0.8),
            (r'(degree|certificate|diploma|qualification|accreditation)', 0.7),
            (r'(material|supply|equipment|tool|resource|software)', 0.7),
            (r'(subscription|membership|fee|payment|scholarship)', 0.8)
        ])
        
        # Personal Care patterns
        self.add_patterns('Personal Care', [
            (r'(salon|spa|beauty|haircut|cosmetic|personal care)', 1.0),
            (r'(grooming|hair|nail|skin|facial|massage)', 0.9),
            (r'(treatment|therapy|product|item|supply|tool)', 0.8),
            (r'(equipment|accessory|service|appointment|booking)', 0.7),
            (r'(reservation|visit|professional|specialist|therapist)', 0.7),
            (r'(stylist|technician)', 0.8)
        ])
        
        # Other patterns (default category)
        self.add_patterns('Other', [
            (r'.*', 0.5)  # Match anything with low confidence
        ])
    
    def add_patterns(self, category, patterns):
        """Add patterns for a category with their weights"""
        for pattern, weight in patterns:
            self.category_patterns[category].append((re.compile(pattern, re.IGNORECASE), weight))
            self.category_weights[category] = max(self.category_weights[category], weight)
    
    def load_learned_patterns(self):
        """Load learned patterns from file"""
        learned_patterns_path = os.path.join(settings.BASE_DIR, 'core', 'models', 'learned_patterns.json')
        if os.path.exists(learned_patterns_path):
            try:
                with open(learned_patterns_path, 'r') as f:
                    self.learned_patterns = defaultdict(list, json.load(f))
            except:
                self.learned_patterns = defaultdict(list)
    
    def save_learned_patterns(self):
        """Save learned patterns to file"""
        learned_patterns_path = os.path.join(settings.BASE_DIR, 'core', 'models', 'learned_patterns.json')
        os.makedirs(os.path.dirname(learned_patterns_path), exist_ok=True)
        with open(learned_patterns_path, 'w') as f:
            json.dump(dict(self.learned_patterns), f)
    
    def learn_pattern(self, text, category):
        """Learn a new pattern from user correction"""
        text = self.preprocess_text(text)
        words = text.split()
        
        # Add the full text as a pattern
        self.learned_patterns[category].append({
            'pattern': text,
            'weight': 0.9  # High weight for learned patterns
        })
        
        # Add individual significant words as patterns
        for word in words:
            if len(word) > 3:  # Only learn words longer than 3 characters
                self.learned_patterns[category].append({
                    'pattern': word,
                    'weight': 0.7  # Lower weight for individual words
                })
        
        self.save_learned_patterns()
    
    def get_similarity_score(self, word1, word2):
        """Calculate similarity between two words"""
        return SequenceMatcher(None, word1.lower(), word2.lower()).ratio()
    
    def find_similar_words(self, word, threshold=0.8):
        """Find similar words in existing patterns"""
        similar_words = []
        for category in self.category_patterns:
            for pattern, _ in self.category_patterns[category]:
                pattern_text = pattern.pattern.strip('()|')
                for existing_word in pattern_text.split('|'):
                    if self.get_similarity_score(word, existing_word) > threshold:
                        similar_words.append(existing_word)
        return similar_words
    
    def preprocess_text(self, text):
        """Preprocess text for better categorization"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def get_category_scores(self, text):
        """Get category scores based on pattern matching"""
        if not text:
            return [('Other', 1.0)]
        
        text = self.preprocess_text(text)
        scores = defaultdict(float)
        words = text.split()
        
        # Check learned patterns first
        for category, patterns in self.learned_patterns.items():
            for pattern_data in patterns:
                if pattern_data['pattern'] in text:
                    scores[category] += pattern_data['weight']
        
        # Check predefined patterns
        for category, patterns in self.category_patterns.items():
            category_score = 0.0
            matched_patterns = 0
            
            for pattern, weight in patterns:
                if pattern.search(text):
                    category_score += weight
                    matched_patterns += 1
            
            if matched_patterns > 0:
                scores[category] += category_score / matched_patterns
        
        # Check for similar words if no strong matches found
        if not scores:
            for word in words:
                if len(word) > 3:  # Only check words longer than 3 characters
                    similar_words = self.find_similar_words(word)
                    if similar_words:
                        # Find the category of the similar word
                        for category, patterns in self.category_patterns.items():
                            for pattern, weight in patterns:
                                if any(similar in pattern.pattern for similar in similar_words):
                                    scores[category] += weight * 0.8  # Lower weight for similar words
        
        # If no matches found, return Other category
        if not scores:
            return [('Other', 1.0)]
        
        # Convert scores to list of tuples and sort by score
        suggestions = [(cat, score) for cat, score in scores.items()]
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        # Only return suggestions with score > 0.3
        suggestions = [(cat, score) for cat, score in suggestions if score > 0.3]
        
        if not suggestions:
            return [('Other', 1.0)]
        
        return suggestions

def get_category_suggestions(description):
    """Get category suggestions with confidence scores"""
    categorizer = TransactionCategorizer()
    return categorizer.get_category_scores(description)

def categorize_transaction(description):
    """Categorize a transaction based on its description"""
    suggestions = get_category_suggestions(description)
    return suggestions[0][0]  # Return the highest scoring category

def learn_from_correction(description, correct_category):
    """Learn from user correction by adding to the dataset"""
    dataset_path = os.path.join(settings.BASE_DIR, 'core', 'data', 'transaction_dataset.json')
    
    try:
        # Load existing dataset
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        
        # Add new transaction
        data['transactions'].append({
            'description': description,
            'category': correct_category,
            'keywords': preprocess_text(description).split()
        })
        
        # Save updated dataset
        with open(dataset_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        # Retrain the model with new data
        train_categorizer()
        
    except Exception as e:
        print(f"Error learning from correction: {e}") 
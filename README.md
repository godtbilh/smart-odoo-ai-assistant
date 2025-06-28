# Smart Multilingual AI Assistant for Odoo

A sophisticated AI-powered assistant that transforms from a simple customer lookup form into a fully conversational interface for Odoo ERP management.

## 🚀 Project Evolution

This project demonstrates the evolution from basic Odoo integration to a smart, multilingual AI assistant:

### Phase 1: Basic Odoo Integration
- Simple customer lookup functionality
- Direct database queries
- Form-based interface

### Phase 2: AI-Powered Enhancement
- CrewAI integration for intelligent task handling
- Multi-agent architecture
- Advanced product management

### Phase 3: Smart Conversational Assistant
- Natural language understanding
- Intelligent request routing
- Multilingual support (English, Dutch)
- Rate limit optimization

## 🎯 Current Features

### 🤖 Smart Assistant (`smart_assistant.py`)
- **Natural Language Processing**: Understands conversational requests
- **Intelligent Routing**: Automatically directs requests to appropriate specialists
- **Multi-Domain Support**: Customer service, product management, email communication
- **Rate Limit Protection**: Optimized for API efficiency

### 🔍 Direct Customer Lookup (`simple_customer_lookup.py`)
- **Zero Rate Limits**: Direct Odoo queries without AI overhead
- **Instant Results**: Fast customer information retrieval
- **Complete Data**: Contact details, order history, addresses

### 💰 Cost-Optimized Flow Assistant (`smart_assistant_flow.py`)
- **60-80% Cost Reduction**: Multi-LLM architecture with intelligent routing
- **CrewAI Flow**: Event-driven task processing
- **Smart LLM Selection**: Flash/Pro/Premium models based on complexity
- **Real-time Cost Monitoring**: Track and optimize AI spending

### 🛠️ Organized Tools (`tools/` directory)
- **Modular Architecture**: Clean, reusable components
- **Odoo Connection**: Centralized connection management
- **Customer Tools**: Advanced customer search and data retrieval
- **Multilingual Product Tools**: Product management in multiple languages

## 📋 Requirements

```
crewai>=0.28.8
python-dotenv>=1.0.0
requests>=2.31.0
```

## 🔧 Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd my-first-odoo-agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy the template
cp .env.template .env

# Edit .env with your actual credentials
# - Odoo URL, database, username, password
# - Google API key for Gemini
# - Tavily API key (optional)
```

### 4. API Keys Setup

#### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to your `.env` file

#### Odoo Credentials
1. Use your Odoo instance URL
2. Database name from your Odoo setup
3. Username and password/API key

## 🚀 Usage

### Smart Conversational Assistant
```bash
python smart_assistant.py
```

**Example conversations:**
- "Who is customer Marina?"
- "Update product Inloopdouche 120 with modern design features"
- "Draft a follow-up email to Brico Boncelles in Dutch"

### Direct Customer Lookup (No Rate Limits)
```bash
python simple_customer_lookup.py
```

**Perfect for:**
- Quick customer searches
- Avoiding API rate limits
- Direct Odoo data access

### Cost-Optimized Flow Assistant
```bash
python smart_assistant_flow.py
```

**Features:**
- **60-80% cost reduction** through intelligent LLM routing
- **Flash LLM** for simple tasks (customer lookups, basic queries)
- **Pro LLM** for standard tasks (emails, product descriptions)
- **Premium LLM** only for complex analysis
- **Real-time cost monitoring** and usage analytics

**Test the optimization:**
```bash
python test_cost_optimization.py
```

## 🏗️ Architecture

### Agent Specialists
- **Customer Service Specialist**: Handles customer inquiries and data retrieval
- **Product Management Specialist**: Manages product updates and multilingual content
- **Email Communication Specialist**: Drafts professional emails in multiple languages

### Smart Request Routing
The system automatically analyzes requests and routes them to appropriate specialists:
- Customer keywords → Customer Service
- Product keywords → Product Management  
- Email keywords → Email Communication
- General requests → Best-fit handler

### Rate Limit Optimization
- Reduced API calls per task
- Intelligent delays between requests
- Automatic retry logic
- Fallback to direct tools when needed

## 🔐 Security

- **API Keys Protected**: Never committed to version control
- **Environment Variables**: Secure credential management
- **Template Configuration**: Safe setup examples
- **Gitignore Protection**: Automatic sensitive file exclusion

## 🌍 Multilingual Support

Currently supports:
- **English**: Full functionality
- **Dutch**: Complete product management and communication
- **Extensible**: Architecture ready for additional languages

## 📊 Performance

### Smart Assistant
- **Complex Tasks**: Full AI-powered conversation
- **Rate Limits**: Optimized for API efficiency
- **Best For**: Natural language interactions

### Simple Lookup
- **Zero Rate Limits**: Direct database access
- **Instant Results**: No AI processing overhead
- **Best For**: Quick data retrieval

## 🛠️ Development

### Project Structure
```
my-first-odoo-agent/
├── .env.template          # Environment configuration template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── smart_assistant.py    # Main conversational AI
├── simple_customer_lookup.py  # Direct lookup tool
└── tools/                # Organized tool modules
    ├── odoo_connection.py     # Connection management
    ├── customer_tools.py      # Customer service tools
    └── multilingual_product_tools.py  # Product management
```

### Adding New Features
1. Create tools in the `tools/` directory
2. Add new agents to `smart_assistant.py`
3. Update request routing logic
4. Test with both AI and direct approaches

## 🎯 Use Cases

### Business Operations
- Customer service inquiries
- Product catalog management
- Multilingual content creation
- Order history analysis

### Development & Testing
- API integration testing
- Multilingual system validation
- Performance optimization
- Rate limit management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and business use. Please ensure compliance with Odoo and API provider terms of service.

## 🙏 Acknowledgments

- **Odoo**: Powerful ERP platform
- **CrewAI**: Multi-agent AI framework
- **Google Gemini**: Advanced language model
- **Python Community**: Excellent libraries and tools

---

**Note**: This project demonstrates the evolution from simple form-based interfaces to sophisticated AI-powered conversational systems. Each phase builds upon the previous, showing practical AI integration in business applications.

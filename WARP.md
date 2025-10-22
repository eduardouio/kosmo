# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Kosmo Flowers is an integrated management system for a flower export company. Built with Django 4.2.14 and PostgreSQL, it automates inventory management, order processing, payments, and supplier coordination. The application has a modular architecture with distinct Django apps handling different business domains.

## Essential Commands

### Initial Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR on Windows: venv\Scripts\activate

# Install dependencies
pip install -r app/requeriments.txt

# Install Playwright browsers (required for web scraping features)
playwright install
```

### Database Operations
```bash
# Navigate to Django project root
cd app/src

# Create migrations for all core apps
./manage.py makemigrations accounts partners products trade

# Apply migrations
./manage.py migrate

# Seed initial data (creates superuser, licenses, and test data)
./manage.py sowseed

# Start development server
./manage.py runserver
```

### Development Workflow
```bash
# Single command setup (run from app/src/)
./manage.py makemigrations accounts partners products trade && ./manage.py migrate && ./manage.py sowseed

# Reset database (use with caution!)
# Delete migrations and database
./delete_migrations.sh  # Run from app/ directory
# Then recreate migrations and database as above
```

### Testing
```bash
# Run all tests with pytest (from app/src/)
pytest

# Run specific test file
pytest tests/models/test_Product.py

# Run tests for a specific app
pytest tests/api/
pytest tests/models/

# Run with verbose output
pytest -v

# Run specific test class or method
pytest tests/models/test_Product.py::TestProductModel::test_product_creation
```

### Custom Management Commands
```bash
# Seed database with initial data
./manage.py sowseed

# Export model data
./manage.py export_model orders

# Import data from CSV
./manage.py import_data

# Update invoice payment status
./manage.py update_invoice_payment_status
```

### Production Deployment
```bash
# Restart services (production only)
sudo systemctl daemon-reload
sudo systemctl restart kosmo.service
sudo systemctl restart nginx.service
```

## Architecture Overview

### Project Structure
```
app/src/
├── kosmo/              # Main Django project configuration
│   ├── settings.py     # Uses common/secrets.py for sensitive config
│   └── urls.py         # Root URL configuration
├── accounts/           # User management & authentication
│   ├── models/         # CustomUserModel, License
│   ├── management/     # Custom commands (sowseed, import_data, export_model)
│   └── views/          # User profile, authentication views
├── partners/           # Business partners (customers/suppliers)
│   └── models/         # Partner, Contact, Bank, DAE
├── products/           # Product catalog and inventory
│   └── models/         # Product, StockDay, StockDetail, BoxItems
├── trade/              # Core business transactions
│   ├── models/         # Order, Invoice, Payment, CreditNote
│   └── management/     # Payment status updates
├── reports/            # PDF report generation
│   └── views/          # Invoice, Payment, Balance, CreditNote PDFs
├── sellers/            # Seller-specific interface
│   └── views/          # Seller dashboard, stocks, orders
├── api/                # REST API endpoints
│   ├── trade/          # Trade-specific APIs
│   ├── seller/         # Seller-specific APIs
│   └── users/          # User management APIs
├── common/             # Shared utilities and business logic
│   ├── secrets.py      # Database & API credentials (EXCLUDED from git)
│   ├── BaseModel.py    # Abstract base model with common fields
│   ├── GPT*Processor.py # AI integration for stock analysis
│   ├── middleware.py   # Custom middleware (access logging)
│   └── data/           # CSV data for seeding
└── tests/              # Comprehensive test suite
    ├── api/            # API endpoint tests
    ├── models/         # Model tests
    └── common/         # Utility tests
```

### Core Django Apps
- **accounts**: Custom user authentication with email-based login, license management
- **partners**: Business partner management (customers, suppliers, contacts, banks, DAEs)
- **products**: Product catalog, flower varieties, stock management with daily tracking
- **trade**: Orders, invoices, payments, credit notes with historical tracking
- **reports**: WeasyPrint/ReportLab PDF generation for business documents
- **sellers**: Restricted interface for sales team with commission tracking
- **api**: RESTful endpoints for all business operations

### Data Model Architecture

The system uses a three-tier transaction model:
1. **Orders** (OrderItems → OrderBoxItems): Initial customer/supplier orders
2. **Invoices** (InvoiceItems → InvoiceBoxItems): Confirmed orders become invoices
3. **Payments** (PaymentDetail): Financial settlements linked to invoices

Stock management tracks:
- **StockDay**: Daily inventory snapshots from suppliers
- **StockDetail**: Line items for each flower variety
- **BoxItems**: Individual product boxes with stem counts, pricing, margins

### Key Design Patterns

**Historical Tracking**: Uses `django-simple-history` to track all changes to Orders, Invoices, Stock
- Historical models automatically created for Order, Invoice, Stock models
- Access history via `.history.all()` on any tracked model instance

**Multi-level Nested Models**: 
- Order → OrderItems → OrderBoxItems
- Invoice → InvoiceItems → InvoiceBoxItems
- StockDay → StockDetail → BoxItems

**Custom User Model**: `accounts.CustomUserModel` uses email as username
- Authentication backend: `common.EmailBackEndAuth.EmailBackEndAuth`
- User roles: ADMIN, VENDEDOR (seller), standard staff

**Middleware**:
- `AccessLoggerMiddleware`: Logs all requests to app/logs/
- `crum.CurrentRequestUserMiddleware`: Tracks current user for audit trails

### Database Configuration

Database settings in `common/secrets.py`:
- **PRODUCTION**: `prod_kosmo` database
- **TEST**: `test_kosmo` database  
- **DEVELOPMENT**: `development_kosmo` database (default)

Change active database by modifying `DEFAULT_DB` in `secrets.py`.

### AI Integration

The system uses GPT/Google AI for stock analysis:
- `GPTDirectProcessor`: OpenAI GPT-4 integration
- `GPTGoogleProcessor`: Google Gemini integration
- `GPTDeepSeekProcessor`: DeepSeek integration
- Used for parsing unstructured stock data from suppliers

### Important URLs

Local development URLs:
- Admin: `http://localhost:8000/admin/`
- Grappelli: `http://localhost:8000/grappelli/`
- Sellers Dashboard: `http://localhost:8000/sellers/`
- Sellers Stocks: `http://localhost:8000/sellers/stocks/`
- Sellers Orders: `http://localhost:8000/sellers/orders/`
- New Order: `http://localhost:8000/sellers/orders/create/`
- Invoices: `http://localhost:8000/sellers/invoices/`

## Development Guidelines

### Working with Models

All models inherit from `common.BaseModel.BaseModel` which provides:
- `id`: Primary key
- `is_active`: Soft delete flag
- `created_at`, `updated_at`: Timestamps
- `created_by`, `updated_by`: User tracking
- `get(identifier)`: Class method to fetch by ID or unique field
- `to_dict()`: Serialize to dictionary

Models are organized in subdirectories (e.g., `products/models/`) with `__init__.py` importing all models.

### Migration Workflow

Always specify apps when creating migrations:
```bash
./manage.py makemigrations accounts partners products trade
```

Core apps that require migrations together:
- `accounts` (user models)
- `partners` (business partners)
- `products` (inventory)
- `trade` (transactions)

### Testing Strategy

- Test framework: `pytest` with `pytest-django`
- Configuration: `app/src/pytest.ini`
- Test fixtures: `app/src/conftest.py`
- Use `pytest-mock` for mocking external services
- Integration tests in `tests/api/` test full request/response cycles

### API Development

REST APIs use Django REST Framework:
- Most API views in `app/src/api/` directory
- Serializers in `common/Serializer*.py`
- Custom API permissions via `AdminOnlyMixin`, `SellerOnlyMixin`
- CORS enabled for frontend development (`CORS_ORIGIN_ALLOW_ALL = True` in dev)

### Security Notes

- `common/secrets.py` contains API keys and database passwords (gitignored)
- Never commit secrets to version control
- Default dev password is 'seguro' for seeded users
- Production uses PostgreSQL with strong passwords

### Frontend Integration

- Static files: `app/src/static/`
- Templates: `app/src/templates/`
- JavaScript apps in `static/js/app/`:
  - `app-order.js`: Order management
  - `app-payments.js`: Payment processing
  - `app_collections.js`: Collections management
- Uses Vue.js 3, Bootstrap 5, jQuery, DataTables

### PDF Report Generation

Reports use WeasyPrint and ReportLab:
- All report views in `reports/views/`
- `PDFInvoice`, `PDFPayment`, `PDFCreditNote`, `PDFBalance`
- Reports include company branding and detailed transaction data

### Code Organization Conventions

- Model files use PascalCase: `Product.py`, `Order.py`
- Each model file may contain multiple related models
- API views use descriptive names: `CreateOrderAPI.py`, `UpdateProductAPI.py`
- Utility classes in `common/` use descriptive names: `StockAnalyzer.py`, `MailSender.py`

## Common Tasks

### Adding a New Model
1. Create model file in appropriate `models/` directory
2. Import in `models/__init__.py`
3. Run `./manage.py makemigrations [app_name]`
4. Apply with `./manage.py migrate`
5. Register in `admin.py` if needed

### Creating Custom Management Command
1. Create file in `[app]/management/commands/[command_name].py`
2. Inherit from `BaseCommand`
3. Implement `handle()` method
4. Run with `./manage.py [command_name]`

### Debugging Tips
- Use `ipdb` for debugging (installed in requirements)
- Logs stored in `app/logs/` (created automatically)
- Django debug mode enabled in development
- Check `PATH_LOGS` in settings for log file location

### Resetting Sequences (PostgreSQL)

After manual data manipulation, reset sequences:
```sql
-- Check max ID
SELECT MAX(id) FROM products_product;

-- Check current sequence value
SELECT last_value FROM products_product_id_seq;

-- Reset sequence
SELECT setval('products_product_id_seq', [max_id + 1], false);
```

## Language and Localization

- Default language: Spanish (es-Es)
- Timezone: America/Guayaquil (Ecuador)
- `USE_TZ = False` (timezone-naive datetimes)

## Dependencies Overview

Key Python packages:
- **Django 4.2.14**: Web framework
- **djangorestframework 3.14.0**: REST API
- **psycopg2-binary**: PostgreSQL adapter
- **pytest 7.4.2, pytest-django 4.5.2**: Testing
- **django-simple-history 3.4.0**: Model history tracking
- **Faker 19.0.0**: Test data generation
- **openai, google-generativeai**: AI integration
- **WeasyPrint, reportlab**: PDF generation
- **playwright**: Web scraping/automation
- **gunicorn**: Production WSGI server

## Notes for AI Assistants

- The codebase mixes English and Spanish (comments, variable names)
- Models use soft deletes (`is_active=True/False`) rather than hard deletes
- Always maintain historical tracking when modifying Order/Invoice/Stock models
- User authentication requires `common.EmailBackEndAuth.EmailBackEndAuth` backend
- When creating test data, use `sowseed` command or Faker library patterns
- Stock calculations involve complex business logic in `common/StockDispoQuantity.py`

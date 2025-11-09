## Daily Office Tests

Comprehensive test suite for the Daily Office Morning Prayer Generator.

### Test Coverage

#### Unit Tests

**`test_api_client.py`** - API Client Testing
- Client initialization and configuration
- HTTP request handling
- Error handling (403, 404, invalid JSON)
- Context manager support
- Real API data structure validation
- Tests for all date formats and edge cases

**`test_prayer_generator.py`** - Markdown Generator Testing
- Date and liturgical information formatting
- Line formatting for all types (headings, rubrics, dialogues, etc.)
- HTML scripture reading conversion
- Text indentation handling
- Complete prayer generation
- Special liturgical days (Christmas, Easter, etc.)
- Markdown structure validation

#### Integration Tests

**`test_integration.py`** - End-to-End Workflow Testing
- Complete service initialization
- Full prayer generation workflow
- File saving functionality
- Context manager usage
- Multiple date handling
- Tests with all real sample data
- Special liturgical day workflows

### Running Tests

#### Run All Tests

```bash
# Using the test runner script
./run_tests.sh

# Or directly with unittest
python3 -m unittest discover -s tests -p "test_*.py"
```

#### Run Specific Test File

```bash
python3 -m unittest tests.test_api_client
python3 -m unittest tests.test_prayer_generator
python3 -m unittest tests.test_integration
```

#### Run Specific Test Class

```bash
python3 -m unittest tests.test_api_client.TestDailyOfficeAPIClient
```

#### Run Specific Test Method

```bash
python3 -m unittest tests.test_api_client.TestDailyOfficeAPIClient.test_client_initialization
```

#### Verbose Output

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

### Test Data

Tests use real API sample data from `api_samples/` directory:

- **Office Prayers**: Morning, evening, midday, compline for 5 dates
- **Special Days**: Christmas, Easter, Ash Wednesday
- **Regular Days**: Typical Sundays and weekdays

Sample dates used:
- 2025-03-05 (Ash Wednesday)
- 2025-04-20 (Easter Sunday)
- 2025-11-08 (Regular Saturday)
- 2025-11-23 (Regular Sunday)
- 2025-12-25 (Christmas)

### Test Statistics

- **Total Tests**: 49
- **Unit Tests**: 31
- **Integration Tests**: 18
- **Coverage**: All major components and workflows

### Adding New Tests

When adding new features:

1. **Add unit tests** for individual components
2. **Add integration tests** for workflows
3. **Update this README** with new test descriptions
4. **Ensure all tests pass** before committing

#### Example Test Structure

```python
import unittest
from dailyoffice import YourNewComponent

class TestYourNewComponent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.component = YourNewComponent()

    def test_feature_name(self):
        """Test that feature works correctly."""
        result = self.component.do_something()
        self.assertEqual(result, expected_value)
```

### Continuous Integration

Tests should be run:
- Before every commit
- After pulling changes
- Before creating pull requests
- In CI/CD pipelines (if configured)

### Test Dependencies

- Python 3.8+
- unittest (standard library)
- Mock/patch from unittest.mock
- Real API sample data in `api_samples/`

No additional dependencies required beyond the main application requirements.

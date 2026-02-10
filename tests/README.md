# Facebook Ads Manager - Test Suite

Comprehensive test suite for the Facebook Ads Manager application.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── test_api_client.py       # API client unit tests
├── test_campaign_manager.py # Campaign manager unit tests
├── test_analytics_reporter.py # Analytics reporter unit tests
├── test_budget_optimizer.py # Budget optimizer unit tests
├── test_ab_testing.py       # A/B testing unit tests
├── test_integration.py      # Integration tests
└── README.md               # This file
```

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run with Coverage Report

```bash
pytest --cov=src --cov-report=html --cov-report=term tests/
```

This will generate:
- Terminal coverage summary
- HTML coverage report in `htmlcov/index.html`

### Run Specific Test Files

```bash
# Test API client only
pytest tests/test_api_client.py

# Test campaign manager only
pytest tests/test_campaign_manager.py

# Test analytics reporter only
pytest tests/test_analytics_reporter.py

# Test budget optimizer only
pytest tests/test_budget_optimizer.py

# Test A/B testing only
pytest tests/test_ab_testing.py

# Test integration scenarios only
pytest tests/test_integration.py
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest tests/test_api_client.py::TestCampaignManagement

# Run a specific test function
pytest tests/test_api_client.py::TestCampaignManagement::test_create_campaign_basic
```

### Run with Verbose Output

```bash
pytest -v tests/
```

### Run with Output Captured

```bash
pytest -s tests/
```

## Test Categories

### Unit Tests

Unit tests focus on testing individual modules in isolation:

- **test_api_client.py**: Tests the FacebookAdsClient wrapper
  - API initialization
  - Campaign CRUD operations
  - Ad set management
  - Insights fetching
  - Error handling

- **test_campaign_manager.py**: Tests the CampaignManager
  - Campaign creation with budget conversion
  - Campaign listing and filtering
  - Campaign operations (pause, activate, update)
  - Campaign duplication
  - Default targeting configuration

- **test_analytics_reporter.py**: Tests the AnalyticsReporter
  - Report generation (campaign and account level)
  - Metrics calculation (CTR, CPC, ROAS, etc.)
  - Anomaly detection
  - CSV export functionality
  - Dashboard display

- **test_budget_optimizer.py**: Tests the BudgetOptimizer
  - Budget optimization algorithms
  - Performance-based budget adjustments
  - Underperformer detection and pausing
  - Portfolio rebalancing
  - Budget limit enforcement

- **test_ab_testing.py**: Tests the ABTestManager
  - A/B test creation and setup
  - Statistical analysis
  - Winner determination with confidence intervals
  - Results display
  - Conversion extraction

### Integration Tests

Integration tests verify complete workflows:

- **test_integration.py**: Tests end-to-end scenarios
  - Campaign creation and monitoring workflow
  - Analytics generation and export workflow
  - Optimization and budget adjustment workflow
  - A/B testing complete lifecycle
  - Multi-campaign management
  - Error handling across modules
  - Performance metrics accuracy

## Fixtures

The `conftest.py` file provides shared fixtures used across tests:

### Configuration Fixtures
- `mock_config`: Mock configuration dictionary
- `mock_config_file`: Temporary config file for testing

### Data Fixtures
- `mock_campaign_data`: Sample campaign data
- `mock_adset_data`: Sample ad set data
- `mock_insights_data`: Sample insights/analytics data
- `mock_insights_with_conversions`: Insights with conversion data
- `mock_insights_no_conversions`: Insights without conversions
- `sample_targeting`: Sample targeting specification

### Mock Object Fixtures
- `mock_facebook_ads_api`: Mocked Facebook API
- `mock_ad_account`: Mocked AdAccount object
- `mock_account_object`: Mocked account with methods
- `mock_campaign_object`: Mocked Campaign object
- `mock_adset_object`: Mocked AdSet object

## Test Coverage Goals

The test suite aims for:
- **>90% code coverage** across all modules
- **100% coverage** of critical paths (campaign creation, budget changes, API calls)
- **Edge case coverage** for error handling and boundary conditions
- **Integration coverage** for complete user workflows

## Mocking Strategy

All tests use mocking to avoid making real API calls:

1. **Facebook API Mocking**: All Facebook Marketing API calls are mocked
2. **No External Dependencies**: Tests don't require API credentials or internet
3. **Deterministic**: Tests produce consistent results
4. **Fast Execution**: Complete suite runs in seconds

## Writing New Tests

When adding new features, follow these guidelines:

1. **Add unit tests** for the new module/function
2. **Add integration tests** if the feature involves multiple modules
3. **Use existing fixtures** from conftest.py when possible
4. **Mock external dependencies** (API calls, file I/O)
5. **Test edge cases** and error conditions
6. **Update this README** if adding new test files

### Example Test Structure

```python
def test_feature_name(self, fixture_name):
    """Test description explaining what is being tested."""
    # Arrange - set up test data and mocks
    mock_obj = Mock()
    mock_obj.method = Mock(return_value=expected_value)

    # Act - execute the code being tested
    result = function_under_test(param)

    # Assert - verify the results
    assert result == expected_value
    mock_obj.method.assert_called_once()
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=src --cov-report=xml tests/

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Debugging Tests

### Run Failed Tests Only

```bash
pytest --lf tests/
```

### Run with PDB on Failure

```bash
pytest --pdb tests/
```

### Show Print Statements

```bash
pytest -s tests/
```

### Stop on First Failure

```bash
pytest -x tests/
```

## Performance Testing

While the current suite focuses on functionality, you can add performance tests:

```bash
# Install pytest-benchmark
pip install pytest-benchmark

# Run with benchmarking
pytest --benchmark-only tests/
```

## Test Maintenance

- **Review tests** when updating dependencies
- **Update mocks** when API changes
- **Refactor tests** to reduce duplication
- **Keep fixtures** up to date with schema changes
- **Document** any test-specific configuration

## Troubleshooting

### Import Errors

If you get import errors, ensure the project is installed:

```bash
pip install -e .
```

### Mock Not Working

Verify the patch path matches the import path used in the source code:

```python
# If source uses: from src.api_client import FacebookAdsApi
# Then patch with: @patch('src.api_client.FacebookAdsApi')
```

### Fixture Not Found

Check that fixtures are defined in `conftest.py` or in the same test file.

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)

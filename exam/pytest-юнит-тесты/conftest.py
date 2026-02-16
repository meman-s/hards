def pytest_configure(config):
    config.addinivalue_line(
        "markers", "fast: быстрые тесты (помечайте быстрые unit-тесты)"
    )
    config.addinivalue_line(
        "markers", "slow: медленные тесты (помечайте тесты, требующие времени)"
    )
    config.addinivalue_line(
        "markers", "integration: интеграционные тесты (помечайте комплексные тесты)"
    )

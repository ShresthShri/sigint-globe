from app.utils.scoring import compute_severity, is_interference


class TestIsInterference:
    def test_below_threshold(self):
        assert is_interference(7) is True
        assert is_interference(0) is True

    def test_at_threshold(self):
        assert is_interference(8) is False

    def test_above_threshold(self):
        assert is_interference(9) is False
        assert is_interference(11) is False

    def test_none(self):
        assert is_interference(None) is False


class TestComputeSeverity:
    def test_clean_cell(self):
        score = compute_severity(interference_ratio=0.0, avg_nac_p=10.0, aircraft_count=5)
        assert score == 0.0

    def test_empty_cell(self):
        score = compute_severity(interference_ratio=0.0, avg_nac_p=0.0, aircraft_count=0)
        assert score == 0.0

    def test_mild_interference(self):
        score = compute_severity(interference_ratio=0.15, avg_nac_p=8.5, aircraft_count=10)
        assert 1.0 <= score <= 2.0

    def test_moderate_interference(self):
        score = compute_severity(interference_ratio=0.4, avg_nac_p=7.0, aircraft_count=10)
        assert 3.0 <= score <= 4.0

    def test_heavy_interference(self):
        score = compute_severity(interference_ratio=0.8, avg_nac_p=4.0, aircraft_count=8)
        assert 7.0 <= score <= 8.0

    def test_extreme_interference(self):
        score = compute_severity(interference_ratio=1.0, avg_nac_p=1.0, aircraft_count=5)
        assert score >= 9.0

    def test_clamped_to_10(self):
        score = compute_severity(interference_ratio=1.0, avg_nac_p=0.0, aircraft_count=20)
        assert score == 10.0

    def test_your_real_data(self):
        ratio = 2 / 15
        avg = (10 + 9 + 9 + 8 + 9 + 9 + 10 + 10 + 8 + 6 + 9 + 8 + 8 + 8 + 0) / 15
        score = compute_severity(interference_ratio=ratio, avg_nac_p=avg, aircraft_count=15)
        assert 1.0 <= score <= 3.0

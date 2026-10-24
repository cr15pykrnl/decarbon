"""Check numerical contracts of the exploratory models, not paper reproduction."""
import unittest

import numpy as np

from digital_twin.models import (
    calculate_battery_degradation,
    calculate_energy_consumption,
    calculate_npv,
    calculate_total_cost_of_ownership,
    monte_carlo_simulation,
)


class ModelContracts(unittest.TestCase):
    def test_force_times_distance_has_joule_scale(self):
        # Isolate each force term instead of comparing two copies of the formula.
        gravity = calculate_energy_consumption(
            1000, np.pi / 2, 1, 0, rolling_resistance=0,
        )
        self.assertAlmostEqual(gravity, 9810)
        rolling = calculate_energy_consumption(
            1000, 0, 10, 0, rolling_resistance=0.01,
        )
        self.assertAlmostEqual(rolling, 981)
        drag = calculate_energy_consumption(
            0, 0, 10, 2, air_density=1, frontal_area=1, drag_coefficient=1,
        )
        self.assertAlmostEqual(drag, 20)

    def test_degradation_initial_condition_and_decay(self):
        self.assertEqual(calculate_battery_degradation(400, 0), 400)
        self.assertLess(calculate_battery_degradation(400, 5), 400)

    def test_discount_timing_and_sign(self):
        self.assertAlmostEqual(calculate_npv(100, [110], 0.1), 0)
        self.assertAlmostEqual(calculate_total_cost_of_ownership(100, 110, 1, 0.1), 200)
        self.assertEqual(calculate_npv(100, []), -100)

    def test_sampler_returns_parameter_draws_not_evaluated_outcomes(self):
        params = {'price': 5, 'fixed': 10}
        uncertainty = {'price': {'type': 'uniform', 'min': 2, 'max': 3}}
        a = monte_carlo_simulation(params, uncertainty, 8, random_seed=7)
        b = monte_carlo_simulation(params, uncertainty, 8, random_seed=7)
        self.assertEqual(a.tolist(), b.tolist())
        self.assertTrue(all(2 <= row['price'] <= 3 and row['fixed'] == 10 for row in a))
        self.assertEqual(params, {'price': 5, 'fixed': 10})


if __name__ == '__main__':
    unittest.main()

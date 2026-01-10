import unittest

import alpha


class AlphaV2Tests(unittest.TestCase):
    def test_arithmetic_program(self):
        result = alpha.run_program_interactive('x = 6 / 2\n< x')
        self.assertEqual(result, {'done': True, 'output': ['3']})

    def test_division_by_zero_is_reportable(self):
        with self.assertRaisesRegex(RuntimeError, 'division by zero'):
            alpha.run_program_interactive('x = 1 / 0\n< x')


if __name__ == '__main__':
    unittest.main()

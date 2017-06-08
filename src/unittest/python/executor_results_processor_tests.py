from collections import namedtuple

import unittest
from unittest import mock

from twentybn_dl.network import ExecutorResultProcessor


class TestExecutorResultProcessor(unittest.TestCase):

    ANYFAILURE = 0
    ANYSUCCESS = 1
    AnyResult = namedtuple('AnyResult', ['result', 'reason'])

    def setUp(self):
        self.processor = ExecutorResultProcessor(
            (self.ANYFAILURE, self.ANYSUCCESS, ),
            self.ANYFAILURE,
            ('Total failures', 'Total downloads'),
        )

    def test_init(self):
        self.assertEqual(self.processor.possible_results, (0, 1))
        self.assertEqual(self.processor.failure_index, self.ANYFAILURE)
        self.assertEqual(self.processor.result_descriptions,
                         ('Total failures', 'Total downloads'))

    def test_process_empty_result(self):
        results = []
        counts, failures = self.processor.process_results(results)
        self.assertEqual(counts, {0: 0, 1: 0})
        self.assertEqual(failures, [])

    def test_process_result_no_failures(self):
        ok = self.AnyResult(1, 'success')
        results = [ok]
        counts, failures = self.processor.process_results(results)
        self.assertEqual(counts, {0: 0, 1: 1})
        self.assertEqual(failures, [])

    def test_process_result(self):
        ok = self.AnyResult(1, 'success')
        results = [ok, ok, ok, ok, ok, self.AnyResult(0, 'FAILURE')]
        counts, failures = self.processor.process_results(results)
        self.assertEqual(counts, {0: 1, 1: 5})
        self.assertEqual(failures, [self.AnyResult(0, 'FAILURE')])

    @mock.patch('builtins.print')
    def test_print_processed_result(self, mock_print):
        ok = self.AnyResult(1, 'success')
        results = [ok, ok, ok, ok, ok, self.AnyResult(0, 'FAILURE')]
        counts, failures = self.processor.process_results(results)
        self.processor.print_processed_results(counts, failures)
        mock_print.assert_has_calls(
            [mock.call('Total failures: 1'),
             mock.call('Total downloads: 5'),
             mock.call('Failures:'),
             mock.call("[AnyResult(result=0, reason='FAILURE')]")]
        )

    @mock.patch(
        'twentybn_dl.network.ExecutorResultProcessor.process_results')
    @mock.patch(
        'twentybn_dl.network.ExecutorResultProcessor.print_processed_results')
    def test_process_and_print(self,
                               mock_print_processed_results,
                               mock_process_results,
                               ):
        results = [1, 1, 1, 1, 1, self.AnyResult(0, 'FAILURE')]
        counts = {0: 1, 1: 5}
        failures = [self.AnyResult(0, 'FAILURE')]
        mock_process_results.return_value = [counts, failures]
        return_value = self.processor.process_and_print(results)
        self.assertEqual(True, return_value)
        mock_process_results.assert_called_once_with(results)
        mock_print_processed_results.assert_called_once_with(counts, failures)

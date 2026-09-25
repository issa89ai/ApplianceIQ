"""Run from the repository root: python -m unittest data_pipeline.test_guide_branches."""

import unittest

from fastapi import HTTPException

from backend.main import get_branch


class GuideBranchTests(unittest.TestCase):
    def test_heating_choices_load_exact_guides(self):
        for branch_id, title in (
            (479829, "Electric Dryer Not Heating"),
            (479830, "Gas Dryer Not Heating"),
        ):
            with self.subTest(title=title):
                guide = get_branch(478885, branch_id)
                self.assertEqual(guide["wikiid"], branch_id)
                self.assertEqual(guide["title"], title)
                self.assertTrue(guide["causes"])
                self.assertTrue(guide["source"])

    def test_unrelated_guide_cannot_be_selected_as_branch(self):
        with self.assertRaises(HTTPException) as error:
            get_branch(478885, 479762)
        self.assertEqual(error.exception.status_code, 404)

    def test_unknown_parent_is_not_found(self):
        with self.assertRaises(HTTPException) as error:
            get_branch(-1, 479829)
        self.assertEqual(error.exception.status_code, 404)

# selenium testing for front end here

import os
import pathlib
import unittest

from selenium import webdriver

# TODO ---- More tests to come.

# function to take a file and get its URI to be able to open it in a browser (for this case it will be chrome)
def file_uri(filename):
    return pathlib.Path(os.path.abspath(filename)).as_uri()


# get the chrome web driver, this is basically initialising it. Notice this is at global level so if we have multiple classes with multiple
# functions in the test file, we can access it from one place
driver = webdriver.Chrome()


# define the class that inherits from unittest.TestCase that will define all the tests to run
class IndexpageTests(unittest.TestCase):


    # then setup class methods according to docs, to startup a webpage and close it after the tests are done before writing tests functions
    @classmethod
    def setUpClass(cls):
        """ Set up browser instance before tests """
        cls.driver = driver
        cls.driver.get(file_uri("index.html"))

    @classmethod
    def tearDownClass(cls):
        """ Close browser after tests """
        cls.driver.quit()


    def test_index_load(self):
        """ check if page loads correctly """
        self.assertIn("Blood Compatibility", self.driver.title)

    # then create more functions to test the actual functionality within index page

    # testing the title of index page
    def test_title(self):
        
        """ check if index page title exists, h1 in this case as it extends layout """
        title_element = driver.find_element_by_tag_name("h1")
        self.assertEqual(title_element.text, "Welcome to the Blood Compatibility App")

    # test the navigation links in navbar and if they exist
    def test_navigation_links(self):

        """ verify navigation links exist """
        links = driver.find_element_by_tag_name("a")
        self.assertGreater(len(links), 0, "No navigation links found")

    # test statistics display
    def test_stats_display(self):

        """ ensure total donors stats are displayed """
        total_donors = driver.find_element_by_id("total-donors").text
        self.assertTrue(total_donors.numeric(), "Total donors count not displayed correctly")


if __name__ == "__main__":
    unittest.main()


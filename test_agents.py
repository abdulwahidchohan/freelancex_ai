#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test script for FreelanceX.AI agents
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import agents directly
from agents import job_search_agent

def main():
    # Test job search agent
    print("Testing job search agent...")
    result = job_search_agent.search_jobs(keywords="web development", budget="$1000-$5000", location="Remote")
    print(result)

if __name__ == "__main__":
    main()
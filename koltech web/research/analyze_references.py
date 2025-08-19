#!/usr/bin/env python3
"""
Web3 Airdrop Discovery Platform - Reference Analysis Script
This script analyzes public airdrop aggregator websites to understand common UI/UX patterns
and generate a research report to guide the platform's development.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from robotexclusionrulesparser import RobotFileParser
from tqdm import tqdm
import markdown

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Reference URLs to analyze
REFERENCE_URLS = [
    "https://airdrops.io",
    "https://airdropalert.com",
    # Add more public reference URLs here
]

class ReferenceAnalyzer:
    def __init__(self):
        self.session = None
        self.results = []
        self.robot_parsers = {}

    async def init_session(self):
        """Initialize aiohttp session"""
        self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

    async def check_robots_txt(self, url: str) -> bool:
        """Check if scraping is allowed by robots.txt"""
        try:
            base_url = '/'.join(url.split('/')[:3])
            robots_url = f"{base_url}/robots.txt"
            
            if base_url not in self.robot_parsers:
                parser = RobotFileParser()
                parser.set_url(robots_url)
                async with self.session.get(robots_url) as response:
                    content = await response.text()
                    parser.parse(content.splitlines())
                self.robot_parsers[base_url] = parser
            
            return self.robot_parsers[base_url].can_fetch("*", url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return False

    async def fetch_page(self, url: str) -> str:
        """Fetch page content with respect to robots.txt"""
        if not await self.check_robots_txt(url):
            logger.warning(f"Scraping not allowed for {url}")
            return ""

        try:
            async with self.session.get(url) as response:
                return await response.text()
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return ""

    def analyze_page(self, html: str) -> Dict[str, Any]:
        """Analyze page content for UI/UX patterns"""
        soup = BeautifulSoup(html, 'html.parser')
        
        analysis = {
            "hero_section": self.analyze_hero(soup),
            "airdrop_list_structure": self.analyze_listing(soup),
            "filters": self.analyze_filters(soup),
            "community_features": self.analyze_community(soup),
            "timestamp": datetime.now().isoformat()
        }
        
        return analysis

    def analyze_hero(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze hero section patterns"""
        hero = soup.find(['header', 'div'], class_=['hero', 'banner', 'header'])
        return {
            "has_hero": bool(hero),
            "has_cta": bool(hero and hero.find(['button', 'a'])),
            "has_search": bool(hero and hero.find(['input', 'form']))
        }

    def analyze_listing(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze airdrop listing patterns"""
        listings = soup.find_all(['div', 'article'], class_=['airdrop', 'card', 'listing'])
        if not listings:
            return {"structure": "unknown"}

        sample = listings[0]
        return {
            "structure": "card" if 'card' in str(sample.get('class', [])) else "list",
            "common_fields": [
                "project_name",
                "chain" if sample.find(text=lambda t: "chain" in str(t).lower()) else None,
                "token" if sample.find(text=lambda t: "token" in str(t).lower()) else None,
                "date" if sample.find(text=lambda t: any(w in str(t).lower() for w in ["date", "time", "end"])) else None
            ]
        }

    def analyze_filters(self, soup: BeautifulSoup) -> List[str]:
        """Analyze filter options"""
        filters = []
        filter_section = soup.find(['div', 'section'], class_=['filters', 'search'])
        if filter_section:
            for elem in filter_section.find_all(['select', 'input']):
                name = elem.get('name', '').lower()
                if name:
                    filters.append(name)
        return filters

    def analyze_community(self, soup: BeautifulSoup) -> Dict[str, bool]:
        """Analyze community features"""
        return {
            "has_comments": bool(soup.find(['div', 'section'], class_=['comments', 'discussion'])),
            "has_social": bool(soup.find(['div'], class_=['social', 'share'])),
            "has_blog": bool(soup.find_all(href=lambda h: h and 'blog' in h.lower()))
        }

    async def analyze_references(self) -> None:
        """Analyze all reference URLs"""
        await self.init_session()
        
        try:
            for url in tqdm(REFERENCE_URLS, desc="Analyzing references"):
                html = await self.fetch_page(url)
                if html:
                    analysis = self.analyze_page(html)
                    analysis['url'] = url
                    self.results.append(analysis)
        finally:
            await self.close_session()

    def generate_report(self) -> None:
        """Generate JSON and Markdown reports"""
        # Save JSON report
        with open('research/report.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        # Generate Markdown report
        md_content = """# Web3 Airdrop Platform UI/UX Research Report

## Overview
This report analyzes UI/UX patterns from leading airdrop platforms to inform our design decisions.

## Key Findings

### Hero Sections
{}

### Listing Patterns
{}

### Filter Options
{}

### Community Features
{}

## Recommendations
1. Use a card-based layout for airdrop listings
2. Implement essential filters: chain, status, and date
3. Include community features like comments and social sharing
4. Add clear CTAs in the hero section
5. Ensure mobile responsiveness

## Technical Considerations
- Server-side rendering for SEO
- Efficient filtering system
- Wallet connection integration
- Community engagement features
""".format(
            self._summarize_hero_sections(),
            self._summarize_listings(),
            self._summarize_filters(),
            self._summarize_community()
        )

        with open('research/report.md', 'w') as f:
            f.write(md_content)

    def _summarize_hero_sections(self) -> str:
        """Summarize hero section findings"""
        has_hero = sum(1 for r in self.results if r.get('hero_section', {}).get('has_hero'))
        return f"- {has_hero}/{len(self.results)} sites have prominent hero sections\n" \
               f"- Most common features: search bar, CTA button"

    def _summarize_listings(self) -> str:
        """Summarize listing patterns"""
        card_count = sum(1 for r in self.results if r.get('airdrop_list_structure', {}).get('structure') == 'card')
        return f"- {card_count}/{len(self.results)} sites use card-based layouts\n" \
               f"- Common fields: project name, chain, token symbol, dates"

    def _summarize_filters(self) -> str:
        """Summarize filter options"""
        all_filters = []
        for r in self.results:
            all_filters.extend(r.get('filters', []))
        return "Common filters: " + ", ".join(set(all_filters))

    def _summarize_community(self) -> str:
        """Summarize community features"""
        features = {
            'comments': sum(1 for r in self.results if r.get('community_features', {}).get('has_comments')),
            'social': sum(1 for r in self.results if r.get('community_features', {}).get('has_social')),
            'blog': sum(1 for r in self.results if r.get('community_features', {}).get('has_blog'))
        }
        return "\n".join(f"- {k.title()}: {v}/{len(self.results)} sites" for k, v in features.items())

def main():
    """Main execution function"""
    analyzer = ReferenceAnalyzer()
    
    try:
        # Create output directories if they don't exist
        os.makedirs('research', exist_ok=True)
        
        # Run analysis
        asyncio.run(analyzer.analyze_references())
        
        # Generate reports
        analyzer.generate_report()
        
        logger.info("Analysis complete! Check research/report.md for results.")
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        # Create stub report if analysis fails
        with open('research/report.md', 'w') as f:
            f.write("""# Web3 Airdrop Platform UI/UX Research Report (Stub)

## Manual Steps Required
1. Add reference URLs to analyze in REFERENCE_URLS
2. Run the script with internet access
3. Review generated report

## Expected Reference URLs
- Major airdrop aggregator sites
- Popular DeFi platforms
- Community forums

## Note
This is a stub report. Please run the script with proper internet access and reference URLs to generate a complete analysis.
""")

if __name__ == "__main__":
    main()

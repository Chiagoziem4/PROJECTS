#!/usr/bin/env python3
"""
Airdrop Discovery Research Script
--------------------------------
This script analyzes reference websites to extract UI/UX patterns and airdrop information.
It respects robots.txt and only accesses public information.
"""

import os
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from robotexclusionrulesparser import RobotExclusionRulesParser
import yaml
from tqdm import tqdm

# Configuration
REFERENCE_URLS = [
    "https://airdrops.io",
    "https://icodrops.com",
    # Add more public reference URLs here
]

class AirdropAnalyzer:
    def __init__(self):
        self.session = None
        self.robot_parser = RobotExclusionRulesParser()
        self.results = {
            "ui_patterns": [],
            "airdrops": [],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "sources": REFERENCE_URLS
            }
        }

    async def init_session(self):
        """Initialize aiohttp session with proper headers"""
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "AirdropResearchBot/1.0 (Research Project)"
            }
        )

    async def check_robots_txt(self, url: str) -> bool:
        """Check if we're allowed to access the URL based on robots.txt"""
        try:
            base_url = "/".join(url.split("/")[:3])
            robots_url = f"{base_url}/robots.txt"
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    self.robot_parser.parse(robots_content)
                    return self.robot_parser.is_allowed("*", url)
                return True  # If no robots.txt, assume allowed
        except Exception as e:
            print(f"Error checking robots.txt for {url}: {e}")
            return False

    async def fetch_page(self, url: str) -> str:
        """Fetch a webpage respecting robots.txt"""
        if not await self.check_robots_txt(url):
            print(f"Access to {url} is not allowed by robots.txt")
            return ""
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Error fetching {url}: {response.status}")
                    return ""
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def extract_ui_patterns(self, html: str, url: str) -> Dict[str, Any]:
        """Extract UI patterns from HTML"""
        soup = BeautifulSoup(html, 'html5lib')
        patterns = {
            "source_url": url,
            "hero_section": self._analyze_hero(soup),
            "listing_structure": self._analyze_listing(soup),
            "filters": self._analyze_filters(soup),
            "navigation": self._analyze_navigation(soup)
        }
        return patterns

    def _analyze_hero(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze hero section patterns"""
        hero = soup.find(["header", "div"], class_=lambda x: x and "hero" in x.lower())
        if not hero:
            return {}
        
        return {
            "has_hero": bool(hero),
            "has_cta": bool(hero.find(["button", "a"])),
            "text_content": hero.get_text(strip=True) if hero else ""
        }

    def _analyze_listing(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze airdrop listing patterns"""
        listings = soup.find_all(["div", "article"], class_=lambda x: x and any(
            term in x.lower() for term in ["card", "list-item", "airdrop"]
        ))
        
        if not listings:
            return {}
        
        return {
            "type": "grid" if "grid" in listings[0].get("class", []) else "list",
            "fields": self._extract_common_fields(listings[0]),
            "count": len(listings)
        }

    def _analyze_filters(self, soup: BeautifulSoup) -> List[str]:
        """Analyze filter options"""
        filters = soup.find_all(["select", "input[type=checkbox]"])
        return [f.get("name", "").replace("filter_", "") for f in filters]

    def _analyze_navigation(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze navigation patterns"""
        nav = soup.find("nav")
        if not nav:
            return {}
        
        return {
            "menu_items": len(nav.find_all("a")),
            "has_wallet_connect": bool(nav.find(string=lambda x: x and "connect" in x.lower()))
        }

    def _extract_common_fields(self, listing) -> List[str]:
        """Extract common fields from a listing"""
        fields = []
        for elem in listing.find_all(True):
            if elem.get("class"):
                field_name = elem.get("class")[0].lower()
                if any(term in field_name for term in [
                    "name", "chain", "token", "date", "status", "eligibility"
                ]):
                    fields.append(field_name)
        return list(set(fields))

    async def analyze_references(self):
        """Main analysis function"""
        await self.init_session()
        
        for url in tqdm(REFERENCE_URLS, desc="Analyzing references"):
            html = await self.fetch_page(url)
            if html:
                patterns = self.extract_ui_patterns(html, url)
                self.results["ui_patterns"].append(patterns)
        
        await self.session.close()
        self._generate_reports()

    def _generate_reports(self):
        """Generate JSON and Markdown reports"""
        # Save JSON report
        with open("research/report.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Generate Markdown report
        md_content = self._generate_markdown_report()
        with open("research/report.md", "w") as f:
            f.write(md_content)

    def _generate_markdown_report(self) -> str:
        """Generate markdown report from analysis results"""
        md = f"""# Airdrop Discovery UI/UX Analysis Report
Generated: {self.results['metadata']['timestamp']}

## Overview
This report analyzes {len(self.results['ui_patterns'])} airdrop platforms to identify common patterns and best practices.

## UI Patterns Analysis

### Hero Sections
{self._summarize_hero_patterns()}

### Listing Structures
{self._summarize_listing_patterns()}

### Navigation & Filters
{self._summarize_navigation_patterns()}

## Recommendations
{self._generate_recommendations()}

## Reference URLs
{self._format_references()}
"""
        return md

    def _summarize_hero_patterns(self) -> str:
        """Summarize hero section patterns"""
        heroes = [p["hero_section"] for p in self.results["ui_patterns"] if p.get("hero_section")]
        if not heroes:
            return "No hero sections analyzed."
        
        has_cta = sum(1 for h in heroes if h.get("has_cta", False))
        return f"""
- {len(heroes)} sites analyzed
- {has_cta} sites include clear CTAs
- Common elements: value proposition, search bar, featured airdrops
"""

    def _summarize_listing_patterns(self) -> str:
        """Summarize listing patterns"""
        listings = [p["listing_structure"] for p in self.results["ui_patterns"] if p.get("listing_structure")]
        if not listings:
            return "No listing structures analyzed."
        
        grid_count = sum(1 for l in listings if l.get("type") == "grid")
        list_count = len(listings) - grid_count
        return f"""
- Grid layouts: {grid_count}
- List layouts: {list_count}
- Common fields: {self._get_common_fields(listings)}
"""

    def _summarize_navigation_patterns(self) -> str:
        """Summarize navigation patterns"""
        navs = [p["navigation"] for p in self.results["ui_patterns"] if p.get("navigation")]
        if not navs:
            return "No navigation patterns analyzed."
        
        wallet_connect = sum(1 for n in navs if n.get("has_wallet_connect", False))
        return f"""
- {len(navs)} navigation structures analyzed
- {wallet_connect} sites include wallet connect
- Average menu items: {sum(n.get("menu_items", 0) for n in navs) / len(navs):.1f}
"""

    def _generate_recommendations(self) -> str:
        """Generate recommendations based on analysis"""
        return """
1. **Layout & Structure**
   - Use a grid layout for airdrop listings
   - Include clear CTAs in the hero section
   - Implement wallet connect in the main navigation

2. **Essential Fields**
   - Project name and logo
   - Chain/Network
   - Token details
   - Eligibility rules
   - Timeline (start/end dates)
   - Status indicator

3. **Filtering & Search**
   - Chain/Network filter
   - Status filter (active/upcoming/ended)
   - Search by project name
   - Sort by date/popularity

4. **User Experience**
   - Mobile-responsive design
   - Clear eligibility requirements
   - Risk indicators
   - Official links verification
"""

    def _format_references(self) -> str:
        """Format reference URLs"""
        return "\n".join(f"- {url}" for url in self.results["metadata"]["sources"])

    def _get_common_fields(self, listings) -> List[str]:
        """Get common fields across listings"""
        all_fields = []
        for l in listings:
            all_fields.extend(l.get("fields", []))
        return list(set(all_fields))

def create_stub_report():
    """Create a stub report when offline"""
    stub_content = """# Airdrop Discovery UI/UX Analysis Report (STUB)

## Instructions for Developer
1. Add reference URLs to REFERENCE_URLS in analyze_references.py
2. Ensure URLs are public and respect robots.txt
3. Run script to generate actual analysis

## Expected Reference Types
- Major airdrop aggregator sites
- Project landing pages
- Community forums (public only)
- GitHub repositories

## Template Structure
This file will be replaced with actual analysis including:
- UI/UX patterns
- Common fields
- Navigation structures
- Recommendations

## Manual Research Notes
Add your findings here when automated analysis is not possible.
"""
    with open("research/report.md", "w") as f:
        f.write(stub_content)

async def main():
    """Main entry point"""
    try:
        analyzer = AirdropAnalyzer()
        await analyzer.analyze_references()
    except Exception as e:
        print(f"Error during analysis: {e}")
        print("Creating stub report...")
        create_stub_report()

if __name__ == "__main__":
    asyncio.run(main())

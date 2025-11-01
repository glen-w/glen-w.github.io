#!/usr/bin/env python3
"""
BibTeX Validator module for process_papers.py
Provides comprehensive BibTeX syntax validation using multiple tools and methods.
"""

import subprocess
import os
import sys
import tempfile
from typing import List, Dict, Tuple, Optional
from pathlib import Path

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.bwriter import BibTexWriter
    BIBTEXPARSER_AVAILABLE = True
except ImportError:
    BIBTEXPARSER_AVAILABLE = False


class BibTeXValidator:
    """Comprehensive BibTeX validation using multiple tools and methods."""
    
    def __init__(self):
        """Initialize the validator with available tools."""
        self.available_tools = self._check_available_tools()
        self.validation_results = {}
    
    def _check_available_tools(self) -> Dict[str, bool]:
        """Check which validation tools are available on the system."""
        tools = {
            'bibtexparser': BIBTEXPARSER_AVAILABLE,
            'bibtex-tidy': self._check_command('bibtex-tidy'),
            'biber': self._check_command('biber'),
            'bibclean': self._check_command('bibclean'),
            'bibcop': self._check_command('bibcop')
        }
        return tools
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available in the system PATH."""
        try:
            result = subprocess.run(
                ['which', command], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def validate_file(self, bibtex_file: str, verbose: bool = False) -> Dict[str, any]:
        """
        Validate a BibTeX file using all available tools.
        
        Args:
            bibtex_file: Path to the BibTeX file to validate
            verbose: Whether to print detailed output
            
        Returns:
            Dictionary with validation results from all tools
        """
        if not os.path.exists(bibtex_file):
            return {
                'error': f'File not found: {bibtex_file}',
                'valid': False,
                'tools_used': []
            }
        
        results = {
            'file': bibtex_file,
            'valid': True,
            'tools_used': [],
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        if verbose:
            print(f"🔍 Validating BibTeX file: {bibtex_file}")
            print(f"📋 Available tools: {[k for k, v in self.available_tools.items() if v]}")
        
        # Run validation with each available tool
        if self.available_tools['bibtexparser']:
            results.update(self._validate_with_bibtexparser(bibtex_file, verbose))
        
        if self.available_tools['bibtex-tidy']:
            results.update(self._validate_with_bibtex_tidy(bibtex_file, verbose))
        
        if self.available_tools['biber']:
            results.update(self._validate_with_biber(bibtex_file, verbose))
        
        if self.available_tools['bibclean']:
            results.update(self._validate_with_bibclean(bibtex_file, verbose))
        
        if self.available_tools['bibcop']:
            results.update(self._validate_with_bibcop(bibtex_file, verbose))
        
        # Overall validation status
        results['valid'] = len(results['errors']) == 0
        
        if verbose:
            if results['valid']:
                print("✅ BibTeX file validation passed")
            else:
                print("❌ BibTeX file validation failed")
                for error in results['errors']:
                    print(f"   Error: {error}")
        
        return results
    
    def _validate_with_bibtexparser(self, bibtex_file: str, verbose: bool = False) -> Dict[str, any]:
        """Validate using bibtexparser library."""
        if not BIBTEXPARSER_AVAILABLE:
            return {'tools_used': []}
        
        try:
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            parser = BibTexParser(common_strings=True)
            parser.ignore_nonstandard_types = False
            parser.homogenize_fields = False
            
            parsed = parser.parse(content)
            
            results = {
                'tools_used': ['bibtexparser'],
                'bibtexparser_entries': len(parsed.entries),
                'bibtexparser_valid': True
            }
            
            if verbose:
                print(f"   📚 bibtexparser: {len(parsed.entries)} entries parsed successfully")
            
            return results
            
        except Exception as e:
            error_msg = f"bibtexparser validation failed: {str(e)}"
            return {
                'tools_used': ['bibtexparser'],
                'bibtexparser_valid': False,
                'errors': [error_msg]
            }
    
    def _validate_with_bibtex_tidy(self, bibtex_file: str, verbose: bool = False) -> Dict[str, any]:
        """Validate using bibtex-tidy tool."""
        try:
            # Run bibtex-tidy in check mode
            result = subprocess.run(
                ['bibtex-tidy', '--check', bibtex_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            results = {
                'tools_used': ['bibtex-tidy'],
                'bibtex_tidy_valid': result.returncode == 0
            }
            
            if result.returncode != 0:
                results['errors'] = [f"bibtex-tidy: {result.stderr.strip()}"]
            elif verbose:
                print("   🧹 bibtex-tidy: File is properly formatted")
            
            return results
            
        except subprocess.TimeoutExpired:
            return {
                'tools_used': ['bibtex-tidy'],
                'errors': ['bibtex-tidy validation timed out']
            }
        except Exception as e:
            return {
                'tools_used': ['bibtex-tidy'],
                'errors': [f"bibtex-tidy validation failed: {str(e)}"]
            }
    
    def _validate_with_biber(self, bibtex_file: str, verbose: bool = False) -> Dict[str, any]:
        """Validate using biber tool."""
        try:
            # Create a temporary .aux file for biber
            with tempfile.NamedTemporaryFile(mode='w', suffix='.aux', delete=False) as aux_file:
                aux_file.write(f"\\citation{{*}}\n\\bibdata{{{bibtex_file.replace('.bib', '')}}}\n")
                aux_file_path = aux_file.name
            
            # Run biber in test mode
            result = subprocess.run(
                ['biber', '--validate-datamodel', '--output-format=bibtex', aux_file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up temporary file
            os.unlink(aux_file_path)
            
            results = {
                'tools_used': ['biber'],
                'biber_valid': result.returncode == 0
            }
            
            if result.returncode != 0:
                results['errors'] = [f"biber: {result.stderr.strip()}"]
            elif verbose:
                print("   🔬 biber: Data model validation passed")
            
            return results
            
        except subprocess.TimeoutExpired:
            return {
                'tools_used': ['biber'],
                'errors': ['biber validation timed out']
            }
        except Exception as e:
            return {
                'tools_used': ['biber'],
                'errors': [f"biber validation failed: {str(e)}"]
            }
    
    def _validate_with_bibclean(self, bibtex_file: str, verbose: bool = False) -> Dict[str, any]:
        """Validate using bibclean tool."""
        try:
            result = subprocess.run(
                ['bibclean', bibtex_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            results = {
                'tools_used': ['bibclean'],
                'bibclean_valid': result.returncode == 0
            }
            
            if result.returncode != 0:
                results['errors'] = [f"bibclean: {result.stderr.strip()}"]
            elif verbose:
                print("   🧽 bibclean: Syntax validation passed")
            
            return results
            
        except subprocess.TimeoutExpired:
            return {
                'tools_used': ['bibclean'],
                'errors': ['bibclean validation timed out']
            }
        except Exception as e:
            return {
                'tools_used': ['bibclean'],
                'errors': [f"bibclean validation failed: {str(e)}"]
            }
    
    def _validate_with_bibcop(self, bibtex_file: str, verbose: bool = False) -> Dict[str, any]:
        """Validate using bibcop tool."""
        try:
            result = subprocess.run(
                ['bibcop', '--check', bibtex_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            results = {
                'tools_used': ['bibcop'],
                'bibcop_valid': result.returncode == 0
            }
            
            if result.returncode != 0:
                results['errors'] = [f"bibcop: {result.stderr.strip()}"]
            elif verbose:
                print("   🔍 bibcop: Quality check passed")
            
            return results
            
        except subprocess.TimeoutExpired:
            return {
                'tools_used': ['bibcop'],
                'errors': ['bibcop validation timed out']
            }
        except Exception as e:
            return {
                'tools_used': ['bibcop'],
                'errors': [f"bibcop validation failed: {str(e)}"]
            }
    
    def get_validation_summary(self, results: Dict[str, any]) -> str:
        """Generate a human-readable validation summary."""
        if not results.get('valid', False):
            return f"❌ Validation failed with {len(results.get('errors', []))} errors"
        
        tools_used = results.get('tools_used', [])
        if not tools_used:
            return "⚠️  No validation tools available"
        
        return f"✅ Validation passed using {', '.join(tools_used)}"
    
    def install_recommended_tools(self) -> List[str]:
        """Provide installation instructions for recommended tools."""
        instructions = []
        
        if not self.available_tools['bibtex-tidy']:
            instructions.append("Install bibtex-tidy: brew install bibtex-tidy")
        
        if not self.available_tools['biber']:
            instructions.append("Install biber: brew install biber")
        
        if not self.available_tools['bibclean']:
            instructions.append("Install bibclean: brew install texlive (includes bibclean)")
        
        return instructions


def main():
    """Command-line interface for BibTeX validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate BibTeX files using multiple tools')
    parser.add_argument('bibtex_file', nargs='?', help='Path to BibTeX file to validate')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--install-tools', action='store_true', help='Show installation instructions')
    
    args = parser.parse_args()
    
    validator = BibTeXValidator()
    
    if args.install_tools:
        instructions = validator.install_recommended_tools()
        if instructions:
            print("Recommended tools to install:")
            for instruction in instructions:
                print(f"  {instruction}")
        else:
            print("All recommended tools are already installed!")
        return
    
    if not args.bibtex_file:
        parser.error("bibtex_file is required unless using --install-tools")
    
    results = validator.validate_file(args.bibtex_file, args.verbose)
    print(validator.get_validation_summary(results))
    
    if not results.get('valid', False):
        sys.exit(1)


if __name__ == "__main__":
    main()
